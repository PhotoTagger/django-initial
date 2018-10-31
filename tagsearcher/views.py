from django.shortcuts import render

# Create your views here.
def tag_search(request):
    context = {}
    if request.method == 'POST':
        context['tag'] = request.POST["tagsearch"]
        return render(request, 'tagged_pictures.html', context)
        # whatever is typed in, will be stored into tag_searched
        # tag_searched = request.POST["tag"]
        # context['tag'] = tag_searched
    return render(request, 'tagsearch.html')

def tagged_pictures(request):
    return render(request, 'tagged_pictures.html')
