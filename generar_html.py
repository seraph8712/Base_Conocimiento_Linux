import json
import re
from html import escape
from pathlib import Path


BASE_DIR = Path(__file__).parent
INPUT_JSON = BASE_DIR / "contenido.json"
TEMPLATE_HTML = BASE_DIR / "templates" / "base.html"
OUTPUT_HTML = BASE_DIR / "output" / "index.html"


def slugify(text: str) -> str:
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


def render_nav(sections: list[dict]) -> str:
    links = []
    for section in sections:
        section_id = section.get("id") or slugify(section["title"])
        links.append(
            f'<a href="#{escape(section_id)}">{escape(section["title"])}</a>'
        )
    return "\n".join(links)


def collect_all_tags(sections: list[dict]) -> list[str]:
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

    return "".join(
        f'<span class="tag">{escape(tag)}</span>'
        for tag in tags
    )


def render_related(related: list[str]) -> str:
    if not related:
        return '<span class="muted">Sin relaciones</span>'

    return "".join(
        f'<li>{escape(item)}</li>'
        for item in related
    )


def build_search_text(item: dict, section_title: str) -> str:
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


def generate_html(data: dict, template: str) -> str:
    title = escape(data.get("title", "Knowledge Base"))
    subtitle = escape(data.get("subtitle", ""))
    intro = data.get("intro", {})
    how_to_use = escape(intro.get("how_to_use", ""))
    scalability = escape(intro.get("scalability", ""))
    sections = data.get("sections", [])

    nav_html = render_nav(sections)
    sections_html = render_sections(sections)
    all_tags = collect_all_tags(sections)
    tag_options_html = render_tag_options(all_tags)

    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{SUBTITLE}}", subtitle)
    html = html.replace("{{INTRO_HOW_TO_USE}}", how_to_use)
    html = html.replace("{{INTRO_SCALABILITY}}", scalability)
    html = html.replace("{{NAV}}", nav_html)
    html = html.replace("{{SECTIONS}}", sections_html)
    html = html.replace("{{TAG_OPTIONS}}", tag_options_html)

    return html


def main() -> None:
    if not INPUT_JSON.exists():
        raise FileNotFoundError(f"No existe el archivo JSON: {INPUT_JSON}")

    if not TEMPLATE_HTML.exists():
        raise FileNotFoundError(f"No existe la plantilla HTML: {TEMPLATE_HTML}")

    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    template = TEMPLATE_HTML.read_text(encoding="utf-8")

    output_html = generate_html(data, template)

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(output_html, encoding="utf-8")

    print(f"Página generada correctamente en: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()