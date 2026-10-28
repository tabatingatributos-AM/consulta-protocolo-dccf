
import json
import os
import secrets
import uuid
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import ProtocoloPublico, PendenciaPublica, DocumentoPublico



def inicio(request):
    """Exibe a página HTML que já existe na raiz do projeto."""
    caminho_html = Path(settings.BASE_DIR) / "index.html"

    if not caminho_html.is_file():
        return HttpResponse(
            "Arquivo index.html não encontrado.",
            status=500,
            content_type="text/plain; charset=utf-8",
        )

    conteudo = caminho_html.read_text(encoding="utf-8")

    return HttpResponse(
        conteudo,
        content_type="text/html; charset=utf-8",
    )


def consultar_protocolo(request, numero, codigo_consulta):
    try:
        protocolo = ProtocoloPublico.objects.get(
            numero=numero,
            codigo_consulta=codigo_consulta,
        )
    except ProtocoloPublico.DoesNotExist:
        return JsonResponse(
            {"erro": "Protocolo não encontrado."},
            status=404,
        )

    pendencias = [
        {
            "descricao": pendencia.descricao,
            "orientacao": pendencia.orientacao,
            "status": pendencia.status,
        }
        for pendencia in protocolo.pendencias.all()
    ]

    documentos = [
        {
            "nome": documento.nome,
            "observacao": documento.observacao,
            "status": documento.status,
        }
        for documento in protocolo.documentos.all()
    ]

    return JsonResponse({
        "numero": protocolo.numero,
        "data_criacao": protocolo.data_criacao.isoformat(),
        "setor": protocolo.setor,
        "situacao": protocolo.situacao,
        "data_atualizacao": protocolo.data_atualizacao.isoformat(),
        "pendencias": pendencias,
        "documentos": documentos,
    })


@csrf_exempt
def sincronizar_protocolo(request):
    if request.method != "POST":
        return JsonResponse(
            {"erro": "Método não permitido."},
            status=405,
        )

    chave_configurada = os.environ.get("SYNC_API_KEY")
    chave_recebida = request.headers.get("Authorization", "")

    if not chave_configurada or not secrets.compare_digest(
        chave_recebida,
        f"Bearer {chave_configurada}",
    ):
        return JsonResponse(
            {"erro": "Não autorizado."},
            status=401,
        )

    try:
        dados = json.loads(request.body)

        numero = str(dados["numero"]).strip()
        codigo_consulta = uuid.UUID(
            str(dados["codigo_consulta"])
        )
        data_criacao = parse_datetime(dados["data_criacao"])
        setor = str(dados["setor"]).strip()
        situacao = str(dados["situacao"]).strip()
        data_atualizacao = parse_datetime(
            dados["data_atualizacao"]
        )

        pendencias = dados.get("pendencias", [])
        documentos = dados.get("documentos", [])

        if (
            not numero
            or not setor
            or not situacao
            or not data_criacao
            or not data_atualizacao
            or not isinstance(pendencias, list)
            or not isinstance(documentos, list)
        ):
            raise ValueError("Dados obrigatórios inválidos.")

        
        for pendencia in pendencias:
            if not isinstance(pendencia, dict):
                raise ValueError("Pendência inválida.")

            if not str(pendencia.get("id", "")).strip():
                raise ValueError("Identificador de pendência ausente.")

            if not str(pendencia.get("descricao", "")).strip():
                raise ValueError("Descrição de pendência ausente.")

            if not isinstance(pendencia.get("status"), str):
                raise ValueError("Status de pendência inválido.")


        for documento in documentos:
            if not isinstance(documento, dict):
                raise ValueError("Documento inválido.")
            if not str(documento.get("id", "")).strip():
                raise ValueError("Identificador de documento ausente.")
            if not str(documento.get("nome", "")).strip():
                raise ValueError("Nome de documento ausente.")
            if not isinstance(documento.get("status"), str):
                raise ValueError("Status de documento inválido.")

    except (
        KeyError,
        ValueError,
        TypeError,
        json.JSONDecodeError,
    ):
        return JsonResponse(
            {"erro": "Dados inválidos ou incompletos."},
            status=400,
        )

    try:
        with transaction.atomic():
            protocolo, criado = (
                ProtocoloPublico.objects.update_or_create(
                    numero=numero,
                    defaults={
                        "codigo_consulta": codigo_consulta,
                        "data_criacao": data_criacao,
                        "setor": setor,
                        "situacao": situacao,
                        "data_atualizacao": data_atualizacao,
                    },
                )
            )

            ids_pendencias_recebidas = []
            for item in pendencias:
                identificador = str(item["id"]).strip()
                ids_pendencias_recebidas.append(identificador)

                PendenciaPublica.objects.update_or_create(
                    protocolo=protocolo,
                    identificador_origem=identificador,
                    defaults={
                        "descricao": str(item["descricao"]).strip(),
                        "orientacao": str(
                            item.get("orientacao", "")
                        ).strip(),
                        "status": str(item["status"]).strip(),
                    },
                )

            ids_documentos_recebidos = []
            for item in documentos:
                identificador = str(item["id"]).strip()
                ids_documentos_recebidos.append(identificador)

                DocumentoPublico.objects.update_or_create(
                    protocolo=protocolo,
                    identificador_origem=identificador,
                    defaults={
                        "nome": str(item["nome"]).strip(),
                        "observacao": str(
                            item.get("observacao", "")
                        ).strip(),
                        "status": str(item["status"]).strip(),
                    },
                )

            # Remove registros que já não existem na origem.
            protocolo.pendencias.exclude(
                identificador_origem__in=ids_pendencias_recebidas
            ).delete()

            protocolo.documentos.exclude(
                identificador_origem__in=ids_documentos_recebidos
            ).delete()

    except (ValueError, TypeError, KeyError):
        return JsonResponse(
            {"erro": "Não foi possível sincronizar os dados."},
            status=400,
        )

    return JsonResponse({
        "mensagem": "Protocolo sincronizado com sucesso.",
        "numero": protocolo.numero,
        "acao": "criado" if criado else "atualizado",
        "total_pendencias": len(pendencias),
        "total_documentos": len(documentos),
    })
