## MODEL

model_list = {
    "1. Sippy by Red1618 [SDXL]": [
        {'url': "https://huggingface.co/Red1618/Zhu/resolve/main/Sippy.safetensors?download=true", 'name': "Sippy.safetensors"}
    ],
    "2. DWXL Inpainting by Remphanstar [SDXL]": [
        {'url': "https://huggingface.co/Remphanstar/Rojos/resolve/main/SDXL-DWXL.fp16.safetensors", 'name': "SDXL-DWXL.fp16-inpainting.safetensors"}
    ],
    "3. Juggernaut XL v9 Inpainting [SDXL]": [
        {'url': "https://civitai.com/api/download/models/907265?type=Model&format=SafeTensor&size=full&fp=fp16", 'name': "juggernautXL_v9Rundiffusionphoto2Inpainting.safetensors"}
    ],
    "4. RealCartoon XL v4 Inpainting [SDXL]": [
        {'url': "https://civitai.com/api/download/models/1024962?type=Model&format=SafeTensor&size=full&fp=fp16", 'name': "realcartoonXL_v4Inpainting.safetensors"}
    ]
}

## VAE

vae_list = {
    "1. SDXL VAE fp16 (ID: 155933)": [
        {'url': "https://civitai.com/api/download/models/155933?type=Model&format=SafeTensor", 'name': "sdxl_vae.safetensors"}
    ],
    "2. Juggernaut VAE (ID: 785437)": [
        {'url': "https://civitai.com/api/download/models/785437?type=Model&format=SafeTensor", 'name': "juggernaut_vae.safetensors"}
    ],
    "3. Default SDXL VAE (ID: 333245)": [
        {'url': "https://civitai.com/api/download/models/333245?type=Model&format=SafeTensor", 'name': "sdxl.vae.safetensors"}
    ]
}

## CONTROLNET

controlnet_list = {
    "1. Kohya Controllite XL Blur": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/kohya_controllllite_xl_blur.safetensors", 'name': "kohya_controllllite_xl_blur.safetensors"},
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/kohya_controllllite_xl_blur_anime.safetensors", 'name': "kohya_controllllite_xl_blur_anime.safetensors"}
    ],
    "2. Kohya Controllite XL Canny": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/kohya_controllllite_xl_canny.safetensors", 'name': "kohya_controllllite_xl_canny.safetensors"},
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/kohya_controllllite_xl_canny_anime.safetensors", 'name': "kohya_controllllite_xl_canny_anime.safetensors"}
    ],
    "3. Kohya Controllite XL Depth": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/kohya_controllllite_xl_depth.safetensors", 'name': "kohya_controllllite_xl_depth.safetensors"},
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/kohya_controllllite_xl_depth_anime.safetensors", 'name': "kohya_controllllite_xl_depth_anime.safetensors"}
    ],
    "4. Kohya Controllite XL Openpose Anime": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/kohya_controllllite_xl_openpose_anime.safetensors", 'name': "kohya_controllllite_xl_openpose_anime.safetensors"},
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/kohya_controllllite_xl_openpose_anime_v2.safetensors", 'name': "kohya_controllllite_xl_openpose_anime_v2.safetensors"}
    ],
    "5. Kohya Controllite XL Scribble Anime": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/kohya_controllllite_xl_scribble_anime.safetensors", 'name': "kohya_controllllite_xl_scribble_anime.safetensors"}
    ],
    "6. T2I Adapter XL Canny": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/t2i-adapter_xl_canny.safetensors", 'name': "t2i-adapter_xl_canny.safetensors"}
    ],
    "7. T2I Adapter XL Openpose": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/t2i-adapter_xl_openpose.safetensors", 'name': "t2i-adapter_xl_openpose.safetensors"}
    ],
    "8. T2I Adapter XL Sketch": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/t2i-adapter_xl_sketch.safetensors", 'name': "t2i-adapter_xl_sketch.safetensors"}
    ],
    "9. T2I Adapter Diffusers XL Canny": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/t2i-adapter_diffusers_xl_canny.safetensors", 'name': "t2i-adapter_diffusers_xl_canny.safetensors"}
    ],
    "10. T2I Adapter Diffusers XL Depth Midas": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/t2i-adapter_diffusers_xl_depth_midas.safetensors", 'name': "t2i-adapter_diffusers_xl_depth_midas.safetensors"}
    ],
    "11. T2I Adapter Diffusers XL Depth Zoe": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/t2i-adapter_diffusers_xl_depth_zoe.safetensors", 'name': "t2i-adapter_diffusers_xl_depth_zoe.safetensors"}
    ],
    "12. T2I Adapter Diffusers XL Lineart": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/t2i-adapter_diffusers_xl_lineart.safetensors", 'name': "t2i-adapter_diffusers_xl_lineart.safetensors"}
    ],
    "13. T2I Adapter Diffusers XL Openpose": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/t2i-adapter_diffusers_xl_openpose.safetensors", 'name': "t2i-adapter_diffusers_xl_openpose.safetensors"}
    ],
    "14. T2I Adapter Diffusers XL Sketch": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/t2i-adapter_diffusers_xl_sketch.safetensors", 'name': "t2i-adapter_diffusers_xl_sketch.safetensors"}
    ],
    "15. IP Adapter SDXL": [
        {'url': "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl.safetensors", 'name': "ip-adapter_sdxl.safetensors"}
    ],
    "16. IP Adapter SDXL VIT-H": [
        {'url': "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter_sdxl_vit-h.safetensors", 'name': "ip-adapter_sdxl_vit-h.safetensors"}
    ],
    "17. Diffusers XL Canny Mid": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/diffusers_xl_canny_mid.safetensors", 'name': "diffusers_xl_canny_mid.safetensors"}
    ],
    "18. Diffusers XL Depth Mid": [
        {'url': "https://huggingface.co/lllyasviel/sd_control_collection/resolve/main/diffusers_xl_depth_mid.safetensors", 'name': "diffusers_xl_depth_mid.safetensors"}
    ],
    "19. Controlnet Union SDXL 1.0": [
        {'url': "https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/resolve/main/diffusion_pytorch_model.safetensors", 'name': "controlnet-union-sdxl-1.0.safetensors"}
    ],
    "20. Controlnet Union SDXL Pro Max": [
        {'url': "https://huggingface.co/xinsir/controlnet-union-sdxl-1.0/resolve/main/diffusion_pytorch_model_promax.safetensors", 'name': "controlnet-union-sdxl-promax.safetensors"}
    ]
}
