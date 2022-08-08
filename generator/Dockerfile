FROM huggingface/transformers-pytorch-gpu:4.21.1
# FROM huggingface/transformers-pytorch-gpu
# FROM nvidia/cuda:11.6.2-cudnn8-devel-ubuntu20.04
WORKDIR /app

RUN pip3 install --upgrade pip
COPY requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir
RUN pip3 install -U jax[cuda11_cudnn82] -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

COPY apikey_by_alex.py /usr/local/lib/python3.8/dist-packages/wandb/sdk/lib/apikey.py

COPY server.py /app
ENTRYPOINT ["python3"]
CMD ["server.py"]