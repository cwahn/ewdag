from django.contrib import admin
from .models import Node, Edge

# Register your models here.


class EdgeAdminInline(admin.TabularInline):
    model = Edge
    extra = 1
    fk_name = "from_node"


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    inlines = [
        EdgeAdminInline,
    ]
