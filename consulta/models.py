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

class PendenciaPublica(models.Model):
    protocolo = models.ForeignKey(
        ProtocoloPublico,
        on_delete=models.CASCADE,
        related_name="pendencias",
    )
    identificador_origem = models.CharField(max_length=50)
    descricao = models.CharField(max_length=250)
    orientacao = models.TextField(blank=True)
    status = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["protocolo", "identificador_origem"],
                name="uniq_pendencia_publica_origem",
            )
        ]

    def __str__(self):
        return f"{self.protocolo.numero} - {self.descricao}"


class DocumentoPublico(models.Model):
    protocolo = models.ForeignKey(
        ProtocoloPublico,
        on_delete=models.CASCADE,
        related_name="documentos",
    )
    identificador_origem = models.CharField(max_length=50)
    nome = models.CharField(max_length=200)
    observacao = models.TextField(blank=True)
    status = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["protocolo", "identificador_origem"],
                name="uniq_documento_publico_origem",
            )
        ]

    def __str__(self):
        return f"{self.protocolo.numero} - {self.nome}"
