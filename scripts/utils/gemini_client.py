"""
Client reutilizavel para API Gemini (imagem e video).
Autenticacao via env var GOOGLE_API_KEY.
"""

import os
import time
import logging

from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Modelos
IMAGE_MODEL = "gemini-2.5-flash-image"
VIDEO_MODEL = "veo-3.1-generate-preview"


def get_client() -> genai.Client:
    """Retorna client autenticado do Gemini."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY nao encontrada. Configure a variavel de ambiente."
        )
    return genai.Client(api_key=api_key)


def generate_image(
    prompt: str,
    reference_image_path: str | None = None,
    output_path: str = "output.png",
    max_retries: int = 3,
) -> str:
    """
    Gera imagem via API Gemini.

    Args:
        prompt: Descricao da imagem a gerar.
        reference_image_path: Caminho para imagem de referencia (opcional).
        output_path: Caminho onde salvar a imagem gerada.
        max_retries: Numero maximo de tentativas em caso de erro.

    Returns:
        Caminho do arquivo salvo.
    """
    client = get_client()
    contents = [prompt]

    if reference_image_path:
        from PIL import Image

        ref_image = Image.open(reference_image_path)
        contents.append(ref_image)
        logger.info(f"Referencia carregada: {reference_image_path}")

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"Gerando imagem (tentativa {attempt}/{max_retries})..."
            )
            response = client.models.generate_content(
                model=IMAGE_MODEL,
                contents=contents,
            )

            for part in response.parts:
                if part.inline_data is not None:
                    image = part.as_image()
                    image.save(output_path)
                    logger.info(f"Imagem salva em: {output_path}")
                    return output_path
                elif part.text is not None:
                    logger.info(f"Texto retornado pelo modelo: {part.text}")

            raise RuntimeError("Nenhuma imagem foi gerada na resposta.")

        except Exception as e:
            logger.error(f"Erro na tentativa {attempt}: {e}")
            if attempt == max_retries:
                raise
            wait = 2**attempt
            logger.info(f"Aguardando {wait}s antes de tentar novamente...")
            time.sleep(wait)

    return output_path


def generate_video(
    prompt: str,
    image_path: str | None = None,
    output_path: str = "output.mp4",
    poll_interval: int = 10,
    max_retries: int = 3,
) -> str:
    """
    Gera video via API Gemini (VEO 3.1).

    Args:
        prompt: Descricao/prompt do video.
        image_path: Caminho para imagem base (frame inicial, opcional).
        output_path: Caminho onde salvar o video gerado.
        poll_interval: Intervalo em segundos entre checks de status.
        max_retries: Numero maximo de tentativas em caso de erro.

    Returns:
        Caminho do arquivo salvo.
    """
    client = get_client()

    kwargs = {
        "model": VIDEO_MODEL,
        "prompt": prompt,
    }

    if image_path:
        from PIL import Image

        ref_image = Image.open(image_path)
        # Converte PIL Image para o formato esperado pela API
        # Primeiro gera um generate_content pra obter o formato correto
        logger.info(f"Imagem base carregada: {image_path}")
        kwargs["image"] = types.Image.from_file(image_path)

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"Iniciando geracao de video (tentativa {attempt}/{max_retries})..."
            )
            operation = client.models.generate_videos(**kwargs)

            logger.info(f"Operacao criada: {operation.name}")
            logger.info("Aguardando conclusao (video e assincrono)...")

            while not operation.done:
                time.sleep(poll_interval)
                operation = client.operations.get(operation)
                logger.info("Ainda processando...")

            generated_video = operation.response.generated_videos[0]
            client.files.download(file=generated_video.video)
            generated_video.video.save(output_path)
            logger.info(f"Video salvo em: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Erro na tentativa {attempt}: {e}")
            if attempt == max_retries:
                raise
            wait = 2**attempt
            logger.info(f"Aguardando {wait}s antes de tentar novamente...")
            time.sleep(wait)

    return output_path
