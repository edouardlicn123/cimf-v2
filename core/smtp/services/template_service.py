# -*- coding: utf-8 -*-
"""
邮件模板服务
"""

from typing import Optional, List, Tuple
from core.smtp.models import EmailTemplate


class TemplateService:
    """邮件模板服务"""

    @classmethod
    def get_template(cls, name: str) -> Optional[EmailTemplate]:
        """获取模板"""
        return EmailTemplate.objects.filter(name=name, is_active=True).first()

    @classmethod
    def render_subject(cls, template: EmailTemplate, context: dict) -> str:
        """渲染邮件主题"""
        subject = template.subject
        for key, value in context.items():
            subject = subject.replace(f'{{{key}}}', str(value))
            subject = subject.replace(f'{{ {key} }}', str(value))
        return subject

    @classmethod
    def render_body(cls, template: EmailTemplate, context: dict) -> Tuple[str, str]:
        """渲染邮件正文，返回 (html, text)"""
        html_body = template.html_body
        text_body = template.text_body
        
        for key, value in context.items():
            placeholder = f'{{{key}}}'
            placeholder_spaced = f'{{ {key} }}'
            html_body = html_body.replace(placeholder, str(value))
            html_body = html_body.replace(placeholder_spaced, str(value))
            text_body = text_body.replace(placeholder, str(value))
            text_body = text_body.replace(placeholder_spaced, str(value))
        
        return html_body, text_body

    @classmethod
    def list_templates(cls) -> List[EmailTemplate]:
        """列出所有模板"""
        return list(EmailTemplate.objects.filter(is_active=True).order_by('-created_at'))

    @classmethod
    def create_template(
        cls,
        name: str,
        subject: str,
        html_body: str,
        text_body: str = '',
        description: str = '',
    ) -> EmailTemplate:
        """创建模板"""
        return EmailTemplate.objects.create(
            name=name,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            description=description,
        )

    @classmethod
    def update_template(
        cls,
        template: EmailTemplate,
        subject: str = None,
        html_body: str = None,
        text_body: str = None,
        description: str = None,
        is_active: bool = None,
    ) -> EmailTemplate:
        """更新模板"""
        if subject is not None:
            template.subject = subject
        if html_body is not None:
            template.html_body = html_body
        if text_body is not None:
            template.text_body = text_body
        if description is not None:
            template.description = description
        if is_active is not None:
            template.is_active = is_active
        template.save()
        return template

    @classmethod
    def delete_template(cls, template: EmailTemplate) -> None:
        """删除模板"""
        template.delete()
