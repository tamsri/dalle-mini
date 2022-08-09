import jax
import jax.numpy as jnp
from dalle_mini import DalleBart, DalleBartProcessor
from vqgan_jax.modeling_flax_vqgan import VQModel
from flax.jax_utils import replicate
from functools import partial
import random
from dalle_mini import DalleBartProcessor
from flax.training.common_utils import shard_prng_key
import numpy as np
from PIL import Image
import os
import logging
import time
import re


def extract_value(filename, pattern):
    """
    Extract value from filename
    :param filename:
    :param pattern:
    :return:
    """
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    else:
        return None


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.info("Starting server")

    # dalle-mega
    DALLE_MODEL = "dalle-mini/dalle-mini/mega-1-fp16:latest"  # can be wandb artifact or 🤗 Hub or local folder or google bucket
    DALLE_COMMIT_ID = None

    # VQGAN model
    VQGAN_REPO = "dalle-mini/vqgan_imagenet_f16_16384"
    VQGAN_COMMIT_ID = "e93a26e7707683d349bf5d5c41c5b0ef69b677a9"

    # check how many devices are available
    logger.info('device count: '+str(jax.local_device_count()))
    logger.info("loading dalle-mini")
    # Load dalle-mini, without showing images
    model, params = DalleBart.from_pretrained(
        DALLE_MODEL, 
        revision=DALLE_COMMIT_ID, 
        dtype=jnp.float16, 
        _do_init=False
    )
    logger.info("loading VQGAN")

    # Load VQGAN
    vqgan, vqgan_params = VQModel.from_pretrained(
        VQGAN_REPO, revision=VQGAN_COMMIT_ID, _do_init=False
    )

    params = replicate(params)
    vqgan_params = replicate(vqgan_params)

    # model inference
    @partial(jax.pmap, axis_name="batch", static_broadcasted_argnums=(3, 4, 5, 6))
    def p_generate(
        tokenized_prompt, key, params, top_k, top_p, temperature, condition_scale
    ):
        return model.generate(
            **tokenized_prompt,
            prng_key=key,
            params=params,
            top_k=top_k,
            top_p=top_p,
            temperature=temperature,
            condition_scale=condition_scale,
        )

    # decode image
    @partial(jax.pmap, axis_name="batch")
    def p_decode(indices, params):
        return vqgan.decode_code(indices, params=params)

    # create a random key
    seed = random.randint(0, 2**32 - 1)
    key = jax.random.PRNGKey(seed)

    processor = DalleBartProcessor.from_pretrained(DALLE_MODEL, revision=DALLE_COMMIT_ID)
    # generate an unique file name
    # file_name = str(uuid.uuid4())
    have_a_job = False

    while True:

        # check is files exists in 'data/requests' folder
        files = os.listdir("./data/requests")
        if len(files) > 0:
            have_a_job = True
            logger.info("Job received!")
            # get the earliest prompt
            prompt_file = sorted(files)[0]
            # read prompt string from file
            with open("./data/requests/"+prompt_file, "r") as f:
                prompts = [f.read()]

            tokenized_prompts = processor(prompts)

            tokenized_prompt = replicate(tokenized_prompts)

            # number of predictions per prompt
            n_predictions = int(extract_value(prompt_file, r'p\[(\d+)\]p'))

            # We can customize generation parameters (see https://huggingface.co/blog/how-to-generate)
            gen_top_k = None
            gen_top_p = None
            temperature = None
            cond_scale = 10.0

            logger.info(f"Prompts: {prompts}\n")
            # generate images
            for i in range(max(n_predictions // jax.device_count(), 1)):
                # pass
                # get a new key
                key, subkey = jax.random.split(key)
                # generate images
                encoded_images = p_generate(
                    tokenized_prompt,
                    shard_prng_key(subkey),
                    params,
                    gen_top_k,
                    gen_top_p,
                    temperature,
                    cond_scale,
                )
                # remove BOS
                encoded_images = encoded_images.sequences[..., 1:]
                # decode images
                decoded_images = p_decode(encoded_images, vqgan_params)
                decoded_images = decoded_images.clip(0.0, 1.0).reshape((-1, 256, 256, 3))
                for decoded_img in decoded_images:
                    img = Image.fromarray(np.asarray(decoded_img * 255, dtype=np.uint8))
                    # save to ./data/generated/
                    img.save('./data/generated/'+prompt_file+'_'+str(i)+'.png')
                # remove file from 'data/requests' folder
                os.remove('./data/requests/'+prompt_file)

        else:
            if have_a_job:
                logger.info("Waiting for a job..")
                have_a_job = False
            time.sleep(1)
            continue


if __name__ == "__main__":
        main()
