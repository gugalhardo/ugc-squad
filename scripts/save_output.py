"""
CLI para salvar outputs de agentes diretamente no Supabase.
Substitui o uso do Write tool para criar arquivos em outputs/.

Comandos:
    # Criar uma nova run (sessao de squad) — retorna run_id
    python scripts/save_output.py create-run --brand tailor --squad ugc --slug google-meet

    # Salvar artefato de texto (markdown, etc)
    python scripts/save_output.py save \\
        --run-id <uuid> \\
        --type hooks \\
        --agent ugc-scriptwriter \\
        --format md \\
        --content "conteudo aqui"

    # Salvar artefato de texto lendo de arquivo temporario
    python scripts/save_output.py save \\
        --run-id <uuid> --type script --agent ugc-scriptwriter --format md --file /tmp/script.md

    # Salvar artefato JSON
    python scripts/save_output.py save \\
        --run-id <uuid> --type veo3_payload --agent ugc-producer --format json \\
        --file /tmp/scene-01.json --scene 1

    # Salvar URL de binario (imagem/video ja no Storage)
    python scripts/save_output.py save \\
        --run-id <uuid> --type image --agent ugc-photographer --format png \\
        --storage-url "https://..." --scene 1

    # Atualizar status de um run
    python scripts/save_output.py update-status --run-id <uuid> --status approved

    # Listar runs de uma marca
    python scripts/save_output.py list --brand tailor --squad ugc

    # Buscar run_id mais recente de uma marca/squad
    python scripts/save_output.py latest --brand tailor --squad ugc

    # Salvar produto CM
    python scripts/save_output.py save-cm-product \\
        --run-id <uuid> --file /tmp/produto.json

    # Salvar referencia CI (anuncio coletado)
    python scripts/save_output.py save-ci-ref \\
        --run-id <uuid> --file /tmp/ads.json --brand tailor --terms "CRM WhatsApp" --country BR
"""

import argparse
import json
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, ".")
from scripts.utils.supabase_client import SupabaseClient


def cmd_create_run(args):
    db = SupabaseClient()
    data = {
        "brand": args.brand,
        "squad": args.squad,
        "status": "draft",
    }
    if args.slug:
        data["slug"] = args.slug
    if args.date:
        data["run_date"] = args.date
    if args.meta:
        data["metadata"] = json.loads(args.meta)

    rows = db.insert("output_runs", data)
    run_id = rows[0]["id"]
    print(run_id)  # stdout limpo para captura por shell
    return run_id


def cmd_save(args):
    db = SupabaseClient()

    content = None
    content_json = None

    # Ler conteudo da fonte correta
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            raw = f.read()
    elif args.content:
        raw = args.content
    elif not args.storage_url:
        # Tentar ler stdin
        raw = sys.stdin.read() if not sys.stdin.isatty() else None
    else:
        raw = None

    if raw is not None:
        if args.format == "json":
            try:
                content_json = json.loads(raw)
            except json.JSONDecodeError:
                content = raw  # fallback: salvar como texto
        else:
            content = raw

    data = {
        "run_id": args.run_id,
        "artifact_type": args.type,
        "agent": args.agent,
        "file_format": args.format,
        "status": "draft",
    }
    if content is not None:
        data["content"] = content
    if content_json is not None:
        data["content_json"] = content_json
    if args.storage_url:
        data["storage_url"] = args.storage_url
    if args.scene:
        data["scene_number"] = args.scene
    if args.variant:
        data["variant_number"] = args.variant
    if args.meta:
        data["metadata"] = json.loads(args.meta)

    rows = db.insert("output_artifacts", data)
    artifact_id = rows[0]["id"]
    print(f"OK: artifact {artifact_id} salvo (run={args.run_id}, type={args.type})")
    return artifact_id


def cmd_update_status(args):
    db = SupabaseClient()
    db.update("output_runs", {"id": f"eq.{args.run_id}"}, {"status": args.status})
    print(f"OK: run {args.run_id} -> {args.status}")


def cmd_list(args):
    db = SupabaseClient()
    params = {"order": "created_at.desc", "limit": str(args.limit)}
    if args.brand:
        params["brand"] = f"eq.{args.brand}"
    if args.squad:
        params["squad"] = f"eq.{args.squad}"
    rows = db.select("output_runs", params=params)
    print(json.dumps(rows, indent=2, ensure_ascii=False, default=str))


def cmd_latest(args):
    db = SupabaseClient()
    params = {
        "order": "created_at.desc",
        "limit": "1",
        "brand": f"eq.{args.brand}",
    }
    if args.squad:
        params["squad"] = f"eq.{args.squad}"
    rows = db.select("output_runs", params=params)
    if not rows:
        print("", end="")
        sys.exit(1)
    print(rows[0]["id"])


def cmd_save_cm_product(args):
    db = SupabaseClient()
    with open(args.file, encoding="utf-8") as f:
        data = json.load(f)

    if args.run_id:
        data["run_id"] = args.run_id

    # Normalizar campos do JSON de produto CM
    record = {
        "run_id": data.get("run_id"),
        "brand": data.get("brand", "confeccoes-mauricio"),
        "product_name": data.get("product_name", data.get("name", "sem nome")),
        "product_url": data.get("product_url", data.get("url")),
        "category": data.get("category"),
        "product_type": data.get("type"),
        "color_data": data.get("color", data.get("color_data")),
        "material_appearance": data.get("material_appearance"),
        "texture": data.get("texture"),
        "fit": data.get("fit"),
        "length": data.get("length"),
        "neckline": data.get("neckline"),
        "sleeves": data.get("sleeves"),
        "details": data.get("details"),
        "accessories_visible": data.get("accessories_visible"),
        "confidence_notes": data.get("confidence_notes"),
        "nano_banana_prompts": data.get("nano_banana_prompts"),
        "instagram_caption": data.get("instagram_caption"),
        "image_urls": data.get("image_urls"),
    }
    # Remover chaves None para nao sobrescrever defaults
    record = {k: v for k, v in record.items() if v is not None}

    rows = db.insert("cm_products", record)
    print(f"OK: cm_product {rows[0]['id']} salvo ({record.get('product_name')})")


def cmd_save_sync(args):
    """Registra mapeamento produto + variantes Vesti ↔ Nuvemshop em ecom_product_sync + ecom_variant_sync."""
    db = SupabaseClient()

    # Upsert produto em ecom_product_sync (unique: brand + vesti_group_id)
    product_data = {
        "brand": args.brand,
        "vesti_group_id": args.vesti_group_id,
    }
    if args.vesti_name:
        product_data["vesti_product_name"] = args.vesti_name
    if args.nuvemshop_product_id:
        product_data["nuvemshop_product_id"] = args.nuvemshop_product_id
    if args.vesti_price is not None:
        product_data["vesti_price"] = args.vesti_price
    if args.nuvemshop_price is not None:
        product_data["nuvemshop_price"] = args.nuvemshop_price
    if args.price_multiplier is not None:
        product_data["price_multiplier"] = args.price_multiplier
    if args.category:
        product_data["category"] = args.category

    product_data["nuvemshop_published"] = True
    product_data["last_sync_at"] = datetime.now(timezone.utc).isoformat()

    rows = db.upsert("ecom_product_sync", product_data)
    product_sync_id = rows[0]["id"]
    print(f"OK: product_sync {product_sync_id} (brand={args.brand}, group={args.vesti_group_id})")

    # Upsert variantes em ecom_variant_sync (unique: brand + vesti_sku)
    if args.variants:
        variants = json.loads(args.variants) if isinstance(args.variants, str) else args.variants
        for v in variants:
            variant_data = {
                "product_sync_id": product_sync_id,
                "brand": args.brand,
                "vesti_sku": v["sku"],
                "color": v.get("color"),
                "size": v.get("size"),
                "in_xml": True,
                "last_seen_at": datetime.now(timezone.utc).isoformat(),
            }
            if v.get("nuvemshop_variant_id"):
                variant_data["nuvemshop_variant_id"] = v["nuvemshop_variant_id"]
            db.upsert("ecom_variant_sync", variant_data)
        print(f"OK: {len(variants)} variantes sincronizadas")

    return product_sync_id


def cmd_save_ci_refs(args):
    """Salva todos os anuncios de um ads.json na tabela ci_references."""
    db = SupabaseClient()
    with open(args.file, encoding="utf-8") as f:
        data = json.load(f)

    ads = data.get("ads", data) if isinstance(data, dict) else data
    search_terms = data.get("search_terms", []) if isinstance(data, dict) else []
    if args.terms:
        search_terms = [t.strip() for t in args.terms.split(",")]

    records = []
    for ad in ads:
        record = {
            "brand": args.brand,
            "search_terms": search_terms,
            "country": args.country or data.get("country", "BR") if isinstance(data, dict) else "BR",
            "ad_id": ad.get("ad_id"),
            "page_name": ad.get("page_name"),
            "ad_status": str(ad.get("status", "")),
            "platforms": ad.get("platforms"),
            "start_date": ad.get("start_date"),
            "format": ad.get("format"),
            "ad_url": ad.get("ad_url"),
            "ad_text": ad.get("ad_text"),
            "cta_type": ad.get("cta_type"),
            "destination_url": ad.get("destination_url"),
            "video_url": ad.get("video_url"),
            "video_transcription": ad.get("video_transcription"),
        }
        if args.run_id:
            record["run_id"] = args.run_id
        records.append({k: v for k, v in record.items() if v is not None})

    if records:
        db.insert("ci_references", records)
    print(f"OK: {len(records)} referencias CI salvas (brand={args.brand})")


def main():
    parser = argparse.ArgumentParser(
        description="Salva outputs de agentes no Supabase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # create-run
    p_create = sub.add_parser("create-run", help="Cria nova sessao de output")
    p_create.add_argument("--brand", required=True)
    p_create.add_argument("--squad", required=True,
                          choices=["ugc", "ci", "cm", "ecom", "traf"])
    p_create.add_argument("--slug", default=None)
    p_create.add_argument("--date", default=None, help="YYYY-MM-DD (default: hoje)")
    p_create.add_argument("--meta", default=None, help="JSON de metadados extras")

    # save
    p_save = sub.add_parser("save", help="Salva artefato de texto/JSON/binario")
    p_save.add_argument("--run-id", required=True, dest="run_id")
    p_save.add_argument("--type", required=True,
                        help="Tipo do artefato (hooks, script, direction, caption, etc.)")
    p_save.add_argument("--agent", required=True)
    p_save.add_argument("--format", default="md",
                        choices=["md", "json", "png", "jpg", "mp4", "txt"])
    p_save.add_argument("--content", default=None, help="Conteudo em texto direto")
    p_save.add_argument("--file", default=None, help="Caminho para arquivo com conteudo")
    p_save.add_argument("--storage-url", default=None, dest="storage_url",
                        help="URL do arquivo no Supabase Storage (imagens/videos)")
    p_save.add_argument("--scene", type=int, default=None)
    p_save.add_argument("--variant", type=int, default=None)
    p_save.add_argument("--meta", default=None, help="JSON de metadados extras")

    # update-status
    p_status = sub.add_parser("update-status", help="Atualiza status de um run")
    p_status.add_argument("--run-id", required=True, dest="run_id")
    p_status.add_argument("--status", required=True,
                          choices=["draft", "approved", "rejected", "published"])

    # list
    p_list = sub.add_parser("list", help="Lista runs")
    p_list.add_argument("--brand", default=None)
    p_list.add_argument("--squad", default=None)
    p_list.add_argument("--limit", type=int, default=20)

    # latest
    p_latest = sub.add_parser("latest", help="Retorna ID do run mais recente")
    p_latest.add_argument("--brand", required=True)
    p_latest.add_argument("--squad", default=None)

    # save-cm-product
    p_cm = sub.add_parser("save-cm-product", help="Salva produto CM no Supabase")
    p_cm.add_argument("--run-id", default=None, dest="run_id")
    p_cm.add_argument("--file", required=True, help="JSON do produto")

    # save-sync
    p_sync = sub.add_parser("save-sync",
                             help="Registra mapeamento produto Vesti ↔ Nuvemshop")
    p_sync.add_argument("--brand", required=True)
    p_sync.add_argument("--vesti-group-id", required=True, dest="vesti_group_id")
    p_sync.add_argument("--vesti-name", default=None, dest="vesti_name")
    p_sync.add_argument("--nuvemshop-product-id", default=None, dest="nuvemshop_product_id")
    p_sync.add_argument("--vesti-price", type=float, default=None, dest="vesti_price")
    p_sync.add_argument("--nuvemshop-price", type=float, default=None, dest="nuvemshop_price")
    p_sync.add_argument("--price-multiplier", type=float, default=None, dest="price_multiplier")
    p_sync.add_argument("--category", default=None)
    p_sync.add_argument("--variants", default=None,
                        help="JSON array de variantes: [{sku, color, size, nuvemshop_variant_id}]")

    # save-ci-refs
    p_ci = sub.add_parser("save-ci-refs",
                           help="Salva anuncios coletados da Meta Ads Library")
    p_ci.add_argument("--run-id", default=None, dest="run_id")
    p_ci.add_argument("--file", required=True, help="ads.json gerado pelo scraper")
    p_ci.add_argument("--brand", required=True)
    p_ci.add_argument("--terms", default=None, help="Termos de busca separados por virgula")
    p_ci.add_argument("--country", default=None)

    args = parser.parse_args()

    dispatch = {
        "create-run": cmd_create_run,
        "save": cmd_save,
        "update-status": cmd_update_status,
        "list": cmd_list,
        "latest": cmd_latest,
        "save-cm-product": cmd_save_cm_product,
        "save-sync": cmd_save_sync,
        "save-ci-refs": cmd_save_ci_refs,
    }
    try:
        dispatch[args.command](args)
    except Exception as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
