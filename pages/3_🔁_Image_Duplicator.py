"""Image Duplicator page for Streamlit app."""

from __future__ import annotations

from io import BytesIO

import streamlit as st

from scrapper.image_duplicator import (
    DuplicateOptions,
    ImageDuplicatorError,
    duplicate_image,
    load_image_from_bytes,
    load_image_from_url,
)


def main() -> None:
    st.set_page_config(
        page_title="Image Duplicator",
        page_icon="🔁",
        layout="wide",
    )

    st.title("🔁 Image Duplicator")
    st.caption(
        "Duplicate an image horizontally or vertically for tiling and pattern creation."
    )

    image_source, settings = render_settings()

    if st.button("Duplicate Image", type="primary", disabled=not image_source):
        run_duplication(image_source, settings)

    render_result()


def render_settings() -> tuple[dict, dict]:
    with st.sidebar:
        st.header("Settings")

        st.subheader("Duplication Configuration")
        direction = st.radio(
            "Direction",
            options=["horizontal", "vertical"],
            index=0,
            help="Choose whether to duplicate the image horizontally (side by side) or vertically (stacked)",
        )

        count = st.number_input(
            "Number of copies",
            min_value=1,
            max_value=50,
            value=3,
            step=1,
            help="How many times to repeat the image in the selected direction",
        )

        st.divider()
        st.subheader("Output")
        st.caption(f"The output will be {count} copies arranged {direction}ly.")

    st.subheader("Image Source")
    input_method = st.radio(
        "Choose input method",
        options=["Upload file", "URL"],
        horizontal=True,
    )

    image_source = None

    if input_method == "Upload file":
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp", "bmp", "gif"],
            help="Select an image file from your computer",
        )
        if uploaded_file:
            image_source = {"type": "file", "data": uploaded_file.getvalue()}

    else:
        image_url = st.text_input(
            "Image URL",
            placeholder="https://example.com/image.jpg",
            help="Enter the URL of the image you want to duplicate",
        )
        if image_url.strip():
            image_source = {"type": "url", "data": image_url.strip()}

    return image_source, {
        "direction": direction,
        "count": int(count),
    }


def run_duplication(image_source: dict, settings: dict) -> None:
    if not image_source:
        st.warning("Please provide an image to duplicate.")
        return

    try:
        with st.spinner("Loading image..."):
            if image_source["type"] == "file":
                image = load_image_from_bytes(image_source["data"])
            else:
                image = load_image_from_url(image_source["data"])

        with st.spinner("Duplicating image..."):
            options = DuplicateOptions(**settings)
            result = duplicate_image(image, options)

    except ImageDuplicatorError as exc:
        st.session_state["duplicate_error"] = str(exc)
        st.session_state["duplicate_result"] = None
        return

    st.session_state["duplicate_result"] = result
    st.session_state["duplicate_error"] = None


def render_result() -> None:
    error = st.session_state.get("duplicate_error")
    result = st.session_state.get("duplicate_result")

    if error:
        st.error(f"Duplication failed: {error}")
        return

    if result is None:
        return

    st.divider()
    st.subheader("Duplication Result")

    render_metrics(result)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("**Original Image**")
        st.image(
            result.original_image,
            caption=f"Size: {result.original_size[0]}×{result.original_size[1]} px",
            use_container_width=True,
        )

    with col2:
        st.markdown("**Duplicated Image**")
        st.image(
            result.duplicated_image,
            caption=f"{result.count} copies {result.direction}ly · {result.new_size[0]}×{result.new_size[1]} px",
            use_container_width=True,
        )

    buf = BytesIO()
    result.duplicated_image.save(buf, format="PNG")
    buf.seek(0)

    st.download_button(
        "Download Duplicated Image",
        data=buf,
        file_name=f"duplicated_image_{result.direction}_{result.count}x.png",
        mime="image/png",
    )


def render_metrics(result) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Direction", result.direction.capitalize())
    col2.metric("Copies", result.count)
    col3.metric("Original Size", f"{result.original_size[0]}×{result.original_size[1]}")
    col4.metric("Final Size", f"{result.new_size[0]}×{result.new_size[1]}")


if __name__ == "__main__":
    main()
