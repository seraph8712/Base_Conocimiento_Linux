import json
import re
from html import escape
from pathlib import Path


BASE_DIR = Path(__file__).parent
TEMPLATE_HTML = BASE_DIR / "templates" / "base.html"
OUTPUT_DIR = BASE_DIR / "output"

# Cada entrada describe una página independiente a generar a partir de su JSON.
PAGES = [
    {
        "key": "linux",
        "label": "Linux",
        "input": BASE_DIR / "contenido_linux.json",
        "output": OUTPUT_DIR / "linux.html",
        "description": "Comandos de sistema, red, SSH, automatizacion, Python y servidor web.",
    },
    {
        "key": "git",
        "label": "Git",
        "input": BASE_DIR / "contenido_git.json",
        "output": OUTPUT_DIR / "git.html",
        "description": "Comandos para versionado, ramas, remotos, historial y flujo de trabajo.",
    },
]


def slugify(text: str) -> str:
    # Convierte títulos como "Red y conectividad" en ids/anchors tipo "red-y-conectividad".
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n",
        "Á": "a", "É": "e", "Í": "i", "Ó": "o", "Ú": "u", "Ñ": "n",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def render_page_links(current_key: str | None = None) -> str:
    # Construye la navegación superior compartida entre portada, Linux y Git.
    links = ['<a href="index.html">Inicio</a>']
    for page in PAGES:
        class_name = ' class="active"' if page["key"] == current_key else ""
        links.append(
            f'<a href="{escape(page["output"].name)}"{class_name}>{escape(page["label"])}</a>'
        )
    return "\n".join(links)


def render_nav(sections: list[dict]) -> str:
    # Genera el menú lateral interno de una página usando sus secciones.
    links = []
    for section in sections:
        section_id = section.get("id") or slugify(section["title"])
        links.append(
            f'<a href="#{escape(section_id)}">{escape(section["title"])}</a>'
        )
    return "\n".join(links)


def collect_all_tags(sections: list[dict]) -> list[str]:
    # Reúne todos los tags únicos para poblar el select de filtros.
    tags = set()
    for section in sections:
        for item in section.get("items", []):
            for tag in item.get("tags", []):
                tags.add(tag)
    return sorted(tags)


def render_tag_options(tags: list[str]) -> str:
    options = ['<option value="">Todos los tags</option>']
    for tag in tags:
        options.append(f'<option value="{escape(tag)}">{escape(tag)}</option>')
    return "\n".join(options)


def render_tags(tags: list[str]) -> str:
    if not tags:
        return '<span class="muted">Sin tags</span>'

    return "".join(f'<span class="tag">{escape(tag)}</span>' for tag in tags)


def render_related(related: list[str]) -> str:
    if not related:
        return '<span class="muted">Sin relaciones</span>'

    return "".join(f"<li>{escape(item)}</li>" for item in related)


def build_search_text(item: dict, section_title: str) -> str:
    # Concatena campos relevantes en un solo texto para que el filtro de búsqueda en JS
    # pueda hacer coincidencias simples con includes().
    parts = [
        item.get("command", ""),
        item.get("description", ""),
        item.get("use_case", ""),
        item.get("problem_solved", ""),
        item.get("example", ""),
        item.get("notes", ""),
        section_title,
        " ".join(item.get("tags", [])),
        " ".join(item.get("related", [])),
        item.get("level", ""),
        item.get("confidence", ""),
    ]
    return " ".join(parts).strip().lower()


def render_items(items: list[dict], section_title: str) -> str:
    # Convierte cada comando del JSON en una tarjeta HTML completa.
    html_parts = []

    for item in items:
        command = escape(item.get("command", ""))
        description = escape(item.get("description", ""))
        use_case = escape(item.get("use_case", ""))
        problem_solved = escape(item.get("problem_solved", ""))
        example = escape(item.get("example", ""))
        level = escape(item.get("level", ""))
        notes = escape(item.get("notes", ""))
        date_learned = escape(item.get("date_learned", ""))
        confidence = escape(item.get("confidence", ""))
        tags = item.get("tags", [])
        tags_html = render_tags(tags)
        related_html = render_related(item.get("related", []))

        data_tags = " ".join(tags).lower()
        data_search = escape(build_search_text(item, section_title))

        html_parts.append(
            f"""
            <article class="item searchable-item" data-tags="{escape(data_tags)}" data-search="{data_search}">
              <div class="label">Comando</div>
              <pre><code>{command}</code></pre>

              <div class="item-grid">
                <div>
                  <div class="label">Descripción</div>
                  <p>{description}</p>
                </div>
                <div>
                  <div class="label">Caso de uso</div>
                  <p>{use_case}</p>
                </div>
              </div>

              <div class="item-grid">
                <div>
                  <div class="label">Problema que resuelve</div>
                  <p>{problem_solved}</p>
                </div>
                <div>
                  <div class="label">Ejemplo</div>
                  <p>{example}</p>
                </div>
              </div>

              <div class="meta-grid">
                <div class="meta-box">
                  <div class="label">Nivel</div>
                  <p>{level}</p>
                </div>
                <div class="meta-box">
                  <div class="label">Confianza</div>
                  <p>{confidence}</p>
                </div>
                <div class="meta-box">
                  <div class="label">Fecha de aprendizaje</div>
                  <p>{date_learned}</p>
                </div>
              </div>

              <div class="extra-grid">
                <div class="extra-box">
                  <div class="label">Notas</div>
                  <p>{notes}</p>
                </div>
                <div class="extra-box">
                  <div class="label">Tags</div>
                  <div class="tags">{tags_html}</div>
                </div>
              </div>

              <div class="related-box">
                <div class="label">Relacionados</div>
                <ul class="related-list">
                  {related_html}
                </ul>
              </div>
            </article>
            """
        )

    return "\n".join(html_parts)


def render_sections(sections: list[dict]) -> str:
    # Agrupa las tarjetas por sección y les asigna un id navegable.
    html_parts = []
    for section in sections:
        section_id = section.get("id") or slugify(section["title"])
        title = escape(section["title"])
        items_html = render_items(section.get("items", []), section["title"])

        html_parts.append(
            f"""
            <section id="{escape(section_id)}" class="card section-card">
              <h2 class="section-title">{title}</h2>
              <div class="items">
                {items_html}
              </div>
            </section>
            """
        )

    return "\n".join(html_parts)


def generate_html(data: dict, template: str, current_page_key: str) -> str:
    # Toma el JSON de una página y reemplaza los placeholders de la plantilla base.
    title = escape(data.get("title", "Knowledge Base"))
    subtitle = escape(data.get("subtitle", ""))
    intro = data.get("intro", {})
    how_to_use = escape(intro.get("how_to_use", ""))
    scalability = escape(intro.get("scalability", ""))
    sections = data.get("sections", [])

    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{SUBTITLE}}", subtitle)
    html = html.replace("{{INTRO_HOW_TO_USE}}", how_to_use)
    html = html.replace("{{INTRO_SCALABILITY}}", scalability)
    html = html.replace("{{PAGE_LINKS}}", render_page_links(current_page_key))
    html = html.replace("{{NAV}}", render_nav(sections))
    html = html.replace("{{SECTIONS}}", render_sections(sections))
    html = html.replace("{{TAG_OPTIONS}}", render_tag_options(collect_all_tags(sections)))
    return html


def generate_index_html() -> str:
    # La portada no usa secciones; solo ofrece accesos rápidos a cada base temática.
    cards = []
    for page in PAGES:
        cards.append(
            f"""
            <a class="home-card" href="{escape(page["output"].name)}">
              <div class="home-card-label">Explorar</div>
              <h2>{escape(page["label"])}</h2>
              <p>{escape(page["description"])}</p>
            </a>
            """
        )

    page_links = render_page_links()
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Knowledge Base</title>
  <link rel="stylesheet" href="../static/styles.css" />
</head>
<body>
  <header>
    <div class="container header-inner">
      <div>
        <h1>Knowledge Base</h1>
        <p class="subtitle">Acceso separado a comandos de Linux y Git.</p>
      </div>
      <nav class="page-links">
        {page_links}
      </nav>
    </div>
  </header>

  <main>
    <div class="container">
      <section class="home-hero card">
        <div>
          <div class="eyebrow">Base separada por tema</div>
          <h2 class="section-title">Elige la guía que quieres consultar</h2>
          <p>Linux conserva comandos de sistema, red, SSH, automatización, Python y Nginx. Git queda aislado para flujo de versionado, ramas, remotos e historial.</p>
        </div>
      </section>

      <section class="home-grid">
        {"".join(cards)}
      </section>
    </div>
  </main>
</body>
</html>
"""


def main() -> None:
    if not TEMPLATE_HTML.exists():
        raise FileNotFoundError(f"No existe la plantilla HTML: {TEMPLATE_HTML}")

    template = TEMPLATE_HTML.read_text(encoding="utf-8")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Recorre la configuración declarativa de PAGES para evitar duplicar lógica.
    for page in PAGES:
        if not page["input"].exists():
            raise FileNotFoundError(f"No existe el archivo JSON: {page['input']}")

        data = json.loads(page["input"].read_text(encoding="utf-8"))
        output_html = generate_html(data, template, page["key"])
        page["output"].write_text(output_html, encoding="utf-8")

    # Además de las páginas de contenido, se genera una portada simple.
    (OUTPUT_DIR / "index.html").write_text(generate_index_html(), encoding="utf-8")
    print(f"Paginas generadas correctamente en: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
