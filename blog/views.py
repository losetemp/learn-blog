#coding: utf-8
#Create your views here.

import markdown
from django.shortcuts import render, get_object_or_404
from comments.forms import CommentForm
from .models import Post, Category, Tag
from django.views.generic import ListView
from django.db.models import Q


class IndexView(ListView):
  model = Post
  template_name = 'blog/index.html'
  context_object_name = 'post_list'


def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    post.increase_views()

    post.body = markdown.markdown(post.body,
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                  ])
    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {'post': post,
                'form': form,
                'comment_list': comment_list
              }
    return render(request, 'blog/detail.html', context=context)

def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month,
                                    )
    return render(request, 'blog/index.html', context={'post_list': post_list})

class CategoryView(IndexView):
  def get_queryset(self):
    cate = get_object_or_404(Category, pk = self.kwargs.get('pk'))
    return super(CategoryView, self).get_queryset().filter(category=cate)

class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)


class IndexView(ListView):
  model = Post
  template_name = 'blog/index.html'
  context_object_name = 'post_list'
  paginate_by = 10

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    paginator = context.get('paginator')
    page = context.get('page_obj')
    is_paginated = context.get('is_paginated')
    pagination_data = self.pagination_data(paginator, page, is_paginated)
    context.update(pagination_data)
    return context

  def pagination_data(self, paginator, page, is_paginated):
    if not is_paginated:
      return {}

    left = []
    right = []

    left_has_more = False
    right_has_more = False
    first = False
    last = False

    page_number = page.number
    total_pages = paginator.num_pages

    page_range = paginator.page_range
    if page_number == 1:
      right = page_range[page_number:page_number + 2]
      if right[-1] < total_pages - 1:
        right_has_more = True
      if right[-1] < total_pages:
        last = True

    elif page_number == total_pages:
      left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]

      if left[0] > 2:
        left_has_more = True

      if left[0] > 1:
        first = True
    
    else:
      left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:page_number - 1]
      right = page_range[page_number:page_number + 2]

      if right[-1] < total_pages - 1:
        right_has_more = True
      if right[-1] < total_pages:
        last = True

      if left[0] > 2:
        left_has_more = True
      if left[0] > 1:
        first = True
    data = {
      'left': left,
      'right': right,
      'left_has_more': left_has_more,
      'right_has_more': right_has_more,
      'first': first,
      'last': last,
    }

    return data

def search(request):
  q = request.GET.get('q')
  error_msg = ''

  if not q:
    error_msg = "请输入关键词"
    return render(request, 'blog/index.html', {'error_msg': error_msg})

  post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
  return render(request, 'blog/index.html', {'error_msg': error_msg,
                                             'post_list': post_list})
