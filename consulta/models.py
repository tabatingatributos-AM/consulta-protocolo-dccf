import uuid
from django.db import models


class ProtocoloPublico(models.Model):
    numero = models.CharField(max_length=30, unique=True)
    codigo_consulta = models.UUIDField(default=uuid.uuid4)
    data_criacao = models.DateTimeField()
    setor = models.CharField(max_length=100)
    situacao = models.CharField(max_length=50)
    data_atualizacao = models.DateTimeField()

    def __str__(self):
        return self.numero