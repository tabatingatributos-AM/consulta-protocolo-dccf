
import json
import os
import secrets

from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt

from .models import ProtocoloPublico


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

    return JsonResponse({
        "numero": protocolo.numero,
        "data_criacao": protocolo.data_criacao.isoformat(),
        "setor": protocolo.setor,
        "situacao": protocolo.situacao,
        "data_atualizacao": protocolo.data_atualizacao.isoformat(),
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
        codigo_consulta = str(dados["codigo_consulta"])
        data_criacao = parse_datetime(dados["data_criacao"])
        setor = str(dados["setor"]).strip()
        situacao = str(dados["situacao"]).strip()
        data_atualizacao = parse_datetime(dados["data_atualizacao"])

        import uuid
        codigo_consulta = uuid.UUID(codigo_consulta)

        if (
            not numero
            or not setor
            or not situacao
            or not data_criacao
            or not data_atualizacao
        ):
            raise ValueError("Dados obrigatórios inválidos.")

    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse(
        {"erro": "Dados inválidos ou incompletos."},
        status=400,
        )

    protocolo, criado = ProtocoloPublico.objects.update_or_create(
        numero=numero,
        defaults={
            "codigo_consulta": codigo_consulta,
            "data_criacao": data_criacao,
            "setor": setor,
            "situacao": situacao,
            "data_atualizacao": data_atualizacao,
        },
    )

    return JsonResponse({
        "mensagem": "Protocolo sincronizado com sucesso.",
        "numero": protocolo.numero,
        "acao": "criado" if criado else "atualizado",
    })
