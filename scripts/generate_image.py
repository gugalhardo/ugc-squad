"""
Gera imagem UGC via API Gemini e salva no Supabase Storage.

Uso (modo Supabase — preferencial):
    python scripts/generate_image.py --prompt "descricao" --run-id <uuid> --scene 1 --agent ugc-photographer

    # Com imagem de referencia
    python scripts/generate_image.py --prompt "descricao" --ref "ref.jpg" --run-id <uuid> --scene 1 --agent ugc-photographer

Retorna (stdout):
    URL publica do arquivo no Storage

Uso (modo legado — sem Supabase):
    python scripts/generate_image.py --prompt "descricao" --output "caminho/output.png"
"""

import argparse
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from scripts.utils.gemini_client import generate_image


def main():
    parser = argparse.ArgumentParser(description="Gera imagem via API Gemini")
    parser.add_argument("--prompt", required=True, help="Prompt para geracao de imagem")
    parser.add_argument("--ref", default=None, help="Caminho para imagem de referencia (opcional)")
    parser.add_argument("--retries", type=int, default=3, help="Numero maximo de tentativas")

    # Modo Supabase (preferencial)
    parser.add_argument("--run-id", default=None, dest="run_id",
                        help="ID do run no Supabase (output_runs.id)")
    parser.add_argument("--agent", default="ugc-photographer",
                        help="Nome do agente que esta gerando a imagem")
    parser.add_argument("--scene", type=int, default=None,
                        help="Numero da cena UGC")
    parser.add_argument("--bucket", default="outputs",
                        help="Bucket no Supabase Storage (default: outputs)")
    parser.add_argument("--storage-path", default=None, dest="storage_path",
                        help="Caminho no bucket (auto-gerado se omitido)")

    # Modo legado
    parser.add_argument("--output", default=None,
                        help="[LEGADO] Caminho local para salvar a imagem")

    args = parser.parse_args()

    use_supabase = args.run_id is not None

    if use_supabase:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            generate_image(
                prompt=args.prompt,
                reference_image_path=args.ref,
                output_path=tmp_path,
                max_retries=args.retries,
            )

            from scripts.utils.supabase_client import SupabaseClient
            db = SupabaseClient()

            if args.storage_path:
                storage_path = args.storage_path
            else:
                scene_suffix = f"scene-{args.scene:02d}" if args.scene else "image"
                storage_path = f"{args.run_id}/{scene_suffix}.png"

            public_url = db.upload_file(args.bucket, storage_path, tmp_path)

            artifact = {
                "run_id": args.run_id,
                "artifact_type": "image",
                "agent": args.agent,
                "file_format": "png",
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
            result = generate_image(
                prompt=args.prompt,
                reference_image_path=args.ref,
                output_path=args.output,
                max_retries=args.retries,
            )
            print(f"OK: {result}")
        except Exception as e:
            print(f"ERRO: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
