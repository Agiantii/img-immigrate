def get_url_file_type(url:str)->str|None:
    common_type = ["jpg","png","jpeg","gif","webp","svg","bmp","ico","tiff"]
    for i in common_type:
        if i in url:
            return i
    return None
