"""
Gera video UGC via API Gemini (VEO 3.1) e salva no Supabase Storage.

Uso (modo Supabase — preferencial):
    python scripts/generate_video.py --prompt "descricao" --run-id <uuid> --scene 1 --agent ugc-producer
    python scripts/generate_video.py --prompt "descricao" --image "frame.png" --run-id <uuid> --scene 1 --agent ugc-producer
    python scripts/generate_video.py --payload "payload.json" --run-id <uuid> --scene 1 --agent ugc-producer

Retorna (stdout):
    URL publica do video no Storage

Uso (modo legado — sem Supabase):
    python scripts/generate_video.py --prompt "descricao" --output "caminho/video.mp4"
    python scripts/generate_video.py --payload "payload.json" --output "caminho/video.mp4"
"""

import argparse
import json
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.utils.gemini_client import generate_video


def main():
    parser = argparse.ArgumentParser(description="Gera video via API Gemini (VEO 3.1)")
    parser.add_argument("--prompt", default=None, help="Prompt para geracao de video")
    parser.add_argument("--image", default=None, help="Caminho para imagem base (frame inicial)")
    parser.add_argument("--payload", default=None, help="Caminho para JSON com prompt e configs")
    parser.add_argument("--poll-interval", type=int, default=10,
                        help="Intervalo de polling em segundos")
    parser.add_argument("--retries", type=int, default=3, help="Numero maximo de tentativas")

    # Modo Supabase (preferencial)
    parser.add_argument("--run-id", default=None, dest="run_id",
                        help="ID do run no Supabase (output_runs.id)")
    parser.add_argument("--agent", default="ugc-producer",
                        help="Nome do agente que esta gerando o video")
    parser.add_argument("--scene", type=int, default=None,
                        help="Numero da cena UGC")
    parser.add_argument("--bucket", default="outputs",
                        help="Bucket no Supabase Storage (default: outputs)")
    parser.add_argument("--storage-path", default=None, dest="storage_path",
                        help="Caminho no bucket (auto-gerado se omitido)")

    # Modo legado
    parser.add_argument("--output", default=None,
                        help="[LEGADO] Caminho local para salvar o video")

    args = parser.parse_args()

    # Extrair prompt e image_path do payload se fornecido
    prompt = args.prompt
    image_path = args.image

    if args.payload:
        with open(args.payload, "r", encoding="utf-8") as f:
            payload = json.load(f)
        prompt = payload.get("prompt", prompt)
        image_path = payload.get("image_path", image_path)

    if not prompt:
        print("ERRO: --prompt ou --payload com campo 'prompt' e obrigatorio.", file=sys.stderr)
        sys.exit(1)

    use_supabase = args.run_id is not None

    if use_supabase:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            generate_video(
                prompt=prompt,
                image_path=image_path,
                output_path=tmp_path,
                poll_interval=args.poll_interval,
                max_retries=args.retries,
            )

            from scripts.utils.supabase_client import SupabaseClient
            db = SupabaseClient()

            if args.storage_path:
                storage_path = args.storage_path
            else:
                scene_suffix = f"scene-{args.scene:02d}" if args.scene else "video"
                storage_path = f"{args.run_id}/{scene_suffix}.mp4"

            public_url = db.upload_file(args.bucket, storage_path, tmp_path,
                                        content_type="video/mp4") if False else \
                         db.upload_file(args.bucket, storage_path, tmp_path)

            artifact = {
                "run_id": args.run_id,
                "artifact_type": "video",
                "agent": args.agent,
                "file_format": "mp4",
                "storage_url": public_url,
                "status": "draft",
            }
            if args.scene:
                artifact["scene_number"] = args.scene
            db.insert("output_artifacts", artifact)

            print(public_url)

        except Exception as e:
            print(f"ERRO: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    else:
        if not args.output:
            print("ERRO: use --run-id (Supabase) ou --output (legado)", file=sys.stderr)
            sys.exit(1)

        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        try:
            result = generate_video(
                prompt=prompt,
                image_path=image_path,
                output_path=args.output,
                poll_interval=args.poll_interval,
                max_retries=args.retries,
            )
            print(f"OK: {result}")
        except Exception as e:
            print(f"ERRO: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
