from django.db import models
from django.core.exceptions import ValidationError

# EWDAG Edge-Weighted Directed Acyclic Graph


class Node(models.Model):
    name = models.CharField(
        max_length=20,
    )
    child_nodes = models.ManyToManyField(
        to="self",
        through="Edge",
        blank=True,
        related_name="parent_nodes",
        symmetrical=False,
    )

    def __str__(self) -> str:
        return self.name


class Edge(models.Model):
    from_node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="parent_edges",
    )
    to_node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="child_edges",
    )
    weight = models.IntegerField()

    class Meta:
        # Validate no parallel edge
        unique_together = (
            "from_node",
            "to_node",
        )

    def is_acyclic_(self, ref, object) -> bool:
        if object.pk != ref.pk:
            child_nodes = object.child_nodes.all()
            if not child_nodes:
                return True
            else:
                return all(
                    list(
                        map(
                            lambda x:
                            self.is_acyclic_(
                                ref,
                                Node.objects.get(pk=x.pk)
                            ),
                            child_nodes,
                        )
                    )
                )
        else:
            return False

    # Validate no self-referencing node, and acyclicity
    def is_acyclic(self) -> bool:
        return self.is_acyclic_(self.from_node, self.to_node)

    def clean(self) -> None:
        # Validate no self-referencing node, and acyclicity
        if not self.is_acyclic():
            # todo Present cyclic path for convenience 
            raise ValidationError("Cyclic path is not permitted.")
        else:
            return super().clean()

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
