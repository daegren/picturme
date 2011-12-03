'''
Created on Dec 3, 2011

@author: dave
'''
from django.views.decorators.http import require_POST
from annoying.decorators import render_to,ajax_request
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile

from StringIO import StringIO

from PIL import Image
from pixel.image2 import ImageTrans
from pixel.models import UserImage,UserTiles

import hashlib, short_url, base64


def handleImage(imgFile):
    imgFile = imgFile.convert('RGB')
    
    ap = ImageTrans()
    #imgFile.thumbnail((500,500))
    (mosaic,arr) = ap.main(imgFile)
    
    photo = UserImage()
    sio = StringIO()
    mosaic.save(sio,'JPEG')
    
    fn_image = hashlib.md5(sio.getvalue()).hexdigest()+'.jpg'
    photo.image.save(fn_image, ContentFile(sio.getvalue()), save=False)
    
    
    m_copy = mosaic.copy()
    m_copy.thumbnail((500,500))
    sio = StringIO()
    m_copy.save(sio,'JPEG')
    
    fn_image = hashlib.md5(sio.getvalue()).hexdigest()+'.jpg'
    photo.thumbnail.save(fn_image, ContentFile(sio.getvalue()), save=False)
    
    photo.save()
    
    for (pixel_id, xy_list) in arr.iteritems():
            tt = UserTiles(user_image=photo)
            tt.pixel_id = pixel_id
            tt.save()
            
    return photo

@require_POST
@csrf_exempt
@ajax_request
def upload(request):
    ff = request.POST.get('file',False)
    if ff:
        s = base64.decodestring(ff)
        imgFile = Image.open(StringIO(s))
    else:
        ff = request.FILES.get('file',False)
        if ff:
            imgFile = Image.open(StringIO(ff.read()))
    
    if imgFile:
        #s = base64.decodestring(ff)
        #imgFile = Image.open(StringIO(s))
        photo = handleImage(imgFile)
        
        url = '/d/%s' % short_url.encode_url(photo.id)
        return {'success':'True','path':url, 'image': photo.image.url, 'thumbnail': photo.thumbnail.url}
    else:
        return {'success':'False'}