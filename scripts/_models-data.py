## MODEL

model_list = {
    "1. AcornMoarMindBreak [SD1.5]": [
        {'url': "https://huggingface.co/Remphanstar/Rojos/resolve/main/SD.15-AcornMoarMindBreak.safetensors", 'name': "SD.15-AcornMoarMindBreak.safetensors"}
    ],
    "2. Lustify (Inpainting) [SD1.5]": [
        {'url': "https://huggingface.co/RandomGulag/lustifySDXLNSFW_oltINPAINTING/resolve/main/lustifySDXLNSFW_oltINPAINTING.safetensors", 'name': "lustifySDXLNSFW_oltINPAINTING.safetensors"}
    ],
    "3. LazyMix Real Amateur [SD1.5]": [
        {'url': "https://civitai.com/models/10961/lazymix-real-amateur-nudes?modelVersionId=300972", 'name': "lazymix-real-amateur-nudes.safetensors"}
    ],
    "4. Inpainting Model 1 [SD1.5]": [
        {'url': "https://civitai.com/api/download/models/188884?type=Model&format=SafeTensor&size=full&fp=fp16", 'name': "inpainting_model_1.safetensors"}
    ],
    "5. Pornmaster Pro (Inpainting) [SD1.5]": [
        {'url': "https://civitai.com/models/1031352/pornmaster-pro-full-v4-inpainting", 'name': "pornmaster-pro-v4-inpainting.safetensors"}
    ],
    "6. Extra Model 1 [SD1.5]": [
        {'url': "https://civitai.com/api/download/models/179318?type=Model&format=SafeTensor&size=full&fp=fp16", 'name': "extra_model_1.safetensors"}
    ],
    "7. D5K6.0 [SD1.5]": [
        {'url': "https://huggingface.co/Remphanstar/Rojos/resolve/main/D5K6.0.safetensors?download=true", 'name': "D5K6.0.safetensors"}
    ],
    "8. Extra Inpainting Model [SD1.5]": [
        {'url': "https://civitai.com/api/download/models/95864?type=Model&format=SafeTensor&size=pruned&fp=fp16", 'name': "extra_inpainting_model.safetensors"}
    ]
}

## VAE

vae_list = {
    "1. SD1.5 VAE 1": [
        {'url': "https://civitai.com/api/download/models/88156?type=Model&format=SafeTensor", 'name': "sd15_vae_1.safetensors"}
    ],
    "2. SD1.5 VAE 2": [
        {'url': "https://civitai.com/api/download/models/311162?type=Model&format=SafeTensor", 'name': "sd15_vae_2.safetensors"}
    ]
}

## CONTROLNET

controlnet_list = {
    "1. Openpose": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_openpose_fp16.yaml"}
    ],
    "2. Canny": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11p_sd15_canny_fp16.yaml"}
    ],
    "3. Depth": [
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/resolve/main/control_v11f1p_sd15_depth_fp16.safetensors"},
        {'url': "https://huggingface.co/ckpt/ControlNet-v1-1/raw/main/control_v11f1p_sd15_depth_fp16.yaml"}
    ]
}
