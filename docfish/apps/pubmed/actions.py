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

from django.contrib.auth.models import User
from docfish.apps.main.models import Collection
from docfish.apps.main.utils import get_collection
from docfish.apps.pubmed.tasks import add_storage_articles

from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.http.response import (
    HttpResponseRedirect, 
    HttpResponseForbidden, 
    Http404
)

import pickle
import json
import os



@login_required
def add_papers(request,cid):
    '''add papers to a collection from a pmid post. if the papers are not added to the collection
    already.
    '''
    collection = get_collection(cid)
    if request.user == collection.owner or request.user in collection.contributors.all():

        if request.method == 'POST':
            try:
                pmids = json.loads(request.POST.get('pmids'))
            except:
                return JsonResponse({"error": "error parsing array!"})

        current_pmids = [e.uid for e in collection.entity_set.all()]

        for pmid in pmids:

            new_pmids = []
            if pmid not in current_pmids:
                new_pmids.append(pmid)

            # Add to collection (NOTE this will eventually be a task
            add_storage_articles(pmids=new_pmids,
                                 cid=collection.id)
            #add_storage_articles.apply_async(kwargs={'pmids':new_pmids,'cid':collection.id})

            response_data = {'result':new_pmids}
            return JsonResponse(response_data)

    return JsonResponse({"hakuna": "matata"})
