# -*- coding: utf-8 -*-
"""
词汇表视图模块
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from core.decorators import admin_required
from core.models import Taxonomy, TaxonomyItem
from core.services import TaxonomyService


@admin_required
def taxonomies(request):
    """词汇表列表"""
    page_num = request.GET.get('page', 1)
    search = request.GET.get('search', '').strip()
    
    all_taxonomies = Taxonomy.objects.all()
    if search:
        all_taxonomies = all_taxonomies.filter(name__icontains=search)
    
    paginator = Paginator(all_taxonomies, 10)
    page_obj = paginator.get_page(page_num)
    
    return render(request, 'structure/taxonomies/index.html', {
        'taxonomies': page_obj.object_list,
        'page_obj': page_obj,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_prev': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'active_section': 'taxonomies',
        'search': search,
    })


@admin_required
def taxonomy_create(request):
    """创建词汇表"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name or not slug:
            messages.error(request, '名称和标识不能为空')
            return redirect('core:taxonomies')
        
        Taxonomy.objects.create(
            name=name,
            slug=slug,
            description=description
        )
        messages.success(request, '词汇表创建成功')
        return redirect('core:taxonomies')
    
    return render(request, 'structure/taxonomies/edit.html', {
        'taxonomy': None,
        'active_section': 'taxonomies',
    })


@admin_required
def taxonomy_view(request, taxonomy_id: int):
    """查看词汇表"""
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)
    page_num = request.GET.get('page', 1)
    
    all_items = taxonomy.items.all().order_by('weight', 'name')
    paginator = Paginator(all_items, 10)
    page_obj = paginator.get_page(page_num)
    
    return render(request, 'structure/taxonomies/view.html', {
        'taxonomy': taxonomy,
        'items': page_obj.object_list,
        'page_obj': page_obj,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_prev': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'prev_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'active_section': 'taxonomies',
    })


@admin_required
def taxonomy_edit(request, taxonomy_id: int):
    """编辑词汇表"""
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)
    
    if request.method == 'POST':
        taxonomy.name = request.POST.get('name', '').strip()
        taxonomy.slug = request.POST.get('slug', '').strip()
        taxonomy.description = request.POST.get('description', '').strip()
        
        if not taxonomy.name or not taxonomy.slug:
            messages.error(request, '名称和标识不能为空')
            return redirect('core:taxonomy_edit', taxonomy_id)
        
        taxonomy.save()
        
        messages.success(request, '词汇表更新成功')
        return redirect('core:taxonomies')
    
    return render(request, 'structure/taxonomies/edit.html', {
        'taxonomy': taxonomy,
        'active_section': 'taxonomies',
    })


@admin_required
def taxonomy_delete(request, taxonomy_id: int):
    """删除词汇表"""
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)
    taxonomy.delete()
    messages.success(request, '词汇表已删除')
    return redirect('core:taxonomies')


@admin_required
def taxonomy_item_create(request, taxonomy_id: int):
    """创建词汇项"""
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name:
            TaxonomyService.create_item(taxonomy_id, name, description)
            messages.success(request, '词汇项创建成功')
        
        return redirect('core:taxonomy_view', taxonomy_id)
    
    return redirect('core:taxonomy_view', taxonomy_id)


@admin_required
def taxonomy_item_update(request, taxonomy_id: int, item_id: int):
    """更新词汇项"""
    taxonomy = get_object_or_404(Taxonomy, id=taxonomy_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name:
            item = TaxonomyItem.objects.filter(id=item_id, taxonomy_id=taxonomy_id).first()
            # 调用者已检查 None
            if item:
                TaxonomyService.update_item(item_id, name=name, description=description)
                messages.success(request, '词汇项更新成功')
            else:
                messages.error(request, '词汇项不存在或不属于当前词汇表')
        
        return redirect('core:taxonomy_view', taxonomy_id)
    
    return redirect('core:taxonomy_view', taxonomy_id)


@admin_required
def taxonomy_item_delete(request, taxonomy_id: int, item_id: int):
    """删除词汇项"""
    item = TaxonomyItem.objects.filter(id=item_id, taxonomy_id=taxonomy_id).first()
    if item:
        TaxonomyService.delete_item(item_id)
        messages.success(request, '词汇项已删除')
    else:
        messages.error(request, '词汇项不存在或不属于当前词汇表')
    return redirect('core:taxonomy_view', taxonomy_id)