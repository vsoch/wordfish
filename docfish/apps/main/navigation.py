'''

Copyright (c) 2017 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from docfish.apps.main.models import *
from itertools import chain
from random import choice

#############################################################################################
# Collection Level Selection (Images)
#############################################################################################

def get_contenders(collection,active=True,get_images=True):
    '''get contenders will return contender (images or text) across a set of entities.
    :param collection: the collection to get entities from
    :param active: return active or inactive (default active)
    :param get_images: if true, return images. Else, return text
    '''
    contenders = []
    for entity in collection.entity_set.all():
        if get_images == True:
            image_set = entity.image_entity.exclude(tags__name="pdf")
            contenders = list(chain(contenders,image_set.filter(active=active)))    
        else:
            text_set = entity.text_entity.exclude(tags__name="pdf")
            contenders = list(chain(contenders,text_set.filter(active=active)))
    return contenders


def get_next_to_markup(user,collection,get_images=True,team=None,N=1,skip=None):
    '''get next to markup will return images from a collection that a user has not seen, 
    chosen, from the entities that are available for annotation. From that set, it is a
    random selection
    :param user: the user to filter for
    :param collection: the collection to use
    :param get_images: when True, filter to ImageMarkup. Otherwise will return text.
    '''
    contenders = get_contenders(collection,get_images=get_images)

    # Do we want image or text markups?
    if get_images == True:
        if team:
            previous_markups = ImageMarkup.objects.filter(team=team,image__in=contenders)
        else:
            previous_markups = ImageMarkup.objects.filter(creator=user,image__in=contenders)

    else:
        if team:
            previous_markups = TextMarkup.objects.filter(team=team,text__in=contenders)
        else:
            previous_markups = TextMarkup.objects.filter(creator=user,text__in=contenders)

    # Return a single unseen image or text
    repeat = False
    if team is not None:
        repeat = True
    return get_unseen(contenders=contenders,
                      seen=previous_markups,
                      get_images=get_images,
                      return_number=N,
                      repeat=repeat,                      
                      random_select=not repeat,
                      skip=skip)


def get_next_to_describe(user,collection,get_images=True,team=None,N=1,skip=None):
    '''get next to describe will first return images for entities that a user has not seen,
    and then a random selection
    '''
    contenders = get_contenders(collection,get_images=get_images)

    # Do we want image or text markups?
    if get_images == True:
        if team:
            previous_descriptions = ImageDescription.objects.filter(team=team,image__in=contenders)
        else:
            previous_descriptions = ImageDescription.objects.filter(creator=user,image__in=contenders)
    else:
        if team:
            previous_descriptions = TextDescription.objects.filter(team=team,text__in=contenders)
        else:
            previous_descriptions = TextDescription.objects.filter(creator=user,text__in=contenders)

    # Return a single unseen image or text
    repeat = False
    if team is not None:
        repeat = True
    return get_unseen(contenders=contenders,
                      seen=previous_descriptions,
                      get_images=get_images,
                      return_number=N,
                      repeat=repeat,
                      random_select=not repeat,
                      skip=skip)


def get_next_to_annotate(user,collection,get_images=True,team=None,N=1,skip=None):
    '''get next to annotate will first return images for entities that a user has not seen,
    and then a random selection
    '''
    contenders = get_contenders(collection,get_images=get_images)

    # Do we want image or text markups?
    if get_images == True:
        if team:
            previous_annotations = ImageAnnotation.objects.filter(team=team,image__in=contenders) 
        else:
            previous_annotations = ImageAnnotation.objects.filter(creator=user,image__in=contenders)
    else:
        if team:
            previous_annotations = TextAnnotation.objects.filter(team=team,text__in=contenders)
        else:
            previous_annotations = TextAnnotation.objects.filter(creator=user,text__in=contenders)

    # Return a single unseen image or text
    repeat = False
    if team is not None:
        repeat = True
    return get_unseen(contenders=contenders,
                      seen=previous_annotations,
                      get_images=get_images,
                      return_number=N,
                      repeat=repeat,
                      random_select=not repeat,
                      skip=skip)



#############################################################################################
# Image Filtering
#############################################################################################


def get_unseen(contenders,seen,return_number=None,get_images=True,repeat=False,
               random_select=True,skip=None):
    '''get unseen images will take a set of seen_images and a set of contenders
    and return one (in case of return_single is True) or a set of unseen images
    :param return_single: randomly select from the set
    :param seen: a list of already seen images
    :param contenders: all images to select from
    :param return_number: if None, will return all
    :param repeat: allow the user to select from seen, otherwise return None.
    default is False, the user does not annotate twice.
    :param random_select: if False, take first off list
    :param skip: skip over one or more images (in the case of already being selected)
    '''
    if get_images == True:
        already_seen = [saw.image.id for saw in seen]
    else:
        already_seen = [saw.text.id for saw in seen]

    if skip is not None:
        if not isinstance(skip,list):
            skip = [skip]
        already_seen = already_seen + skip

    remaining = [c for c in contenders if c.id not in already_seen]

    # If there are unseen, filter to them
    if len(remaining) > 0: 
        selection = remaining

    # Otherwise select randomly from all
    else:
        if repeat == False:
            return None
        selection = contenders

    # User wants to return all, or wants more than we have
    if return_number == None or return_number > len(selection):
        return selection
    
    # or randomly select one from it
    choices = []
    for c in range(return_number):
        if random_select:
            idx = choice(range(0,len(selection)))
        else:
            idx = 0
        choices.append(selection.pop(idx))
    if len(choices) == 1:
        return choices[0]
    return choices
