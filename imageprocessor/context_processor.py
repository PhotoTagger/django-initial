import cloudinary


def consts(request):
    return dict(
        CLOUDINARY_CLOUD_NAME = cloudinary.config().cloud_name
    )