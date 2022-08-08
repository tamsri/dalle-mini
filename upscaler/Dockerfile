
# FROM pytorch/manylinux-cuda117
# FROM huggingface/transformers-pytorch-gpu:4.21.1
FROM huggingface/transformers-pytorch-gpu
# FROM nvidia/cuda:11.6.2-cudnn8-devel-ubuntu20.04
WORKDIR /app

RUN pip3 install --upgrade pip

# copy all files recursivelly
COPY . /app
RUN pip3 install basicsr &\
    pip3 install facexlib &\
    pip3 install gfpgan
RUN pip3 install -r requirements.txt --no-cache-dir
RUN python3 setup.py develop
RUN apt-get update -y
RUN apt-get install wget -y
RUN wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -P experiments/pretrained_models

# COPY server.py /app
ENTRYPOINT ["python3"]
CMD ["inference_realesrgan.py"]