from base64 import b64decode, decodebytes
import io
from importlib import import_module
import os
from PIL import Image
from typing import List, Tuple
from uuid import uuid4

from decouple import config

from flask_restful import Resource


def get_routes(modulesDir='modules', version='v1') -> List[Tuple[str, Resource]]:
    """Get the endpoint routes of each module. Transform
    each endpoint into /version/endpoint
    
    Parameters
    ---
    modulesDir: The modules folder
    version: The specific version of the modules

    Return: A list of endpoints where each endpoint is formatted
    to /version/endpoint
    """
    routes = []
    modules = import_module(modulesDir).__all__

    for module in modules:
        try:
            module = import_module(f'{modulesDir}.{module}.urls')
            for url, resource in module.routes:
                url = f"/{version}{url}"
                routes.append((url, resource))
        except ModuleNotFoundError as e:
            pass
    return routes


def is_valid_picture(b64img: str) -> bool:
    """Verify is a string is a valid base64 image
    
    Parameters
    ---
        b64img: A base64 image string
    """
    try:
        img = b64decode(b64img)
        img = Image.open(io.BytesIO(img))
    except Exception:
        return False
    
    if img.format.lower() in ["jpg", "jpeg", "png"]:        
        width, height = img.size
        return True
    else:
        return False

def save_picture(b64img: str) -> str:
    """Save an image and return the filename
    
    Parameters
    ---
        b64img: A base64 image string
    """
    img = b64decode(b64img)
    img = Image.open(io.BytesIO(img))
    ext = img.format.lower()
    api_dir = config('PHOTO_UPLOAD')

    filename = f"{str(uuid4()).replace('-', '')}.{ext}"
    filepath = os.path.join(api_dir, filename)

    if not os.path.exists(api_dir):
        os.mkdir(api_dir)

    img.save(filepath, ext)

    return filename


def remove_picture(filename: str):
    """Remove a photo from the photo folder"""
    try:
        api_dir = config('PHOTO_UPLOAD')
        filepath = os.path.join(api_dir, filename)
        os.remove(filepath)
    except:
        pass