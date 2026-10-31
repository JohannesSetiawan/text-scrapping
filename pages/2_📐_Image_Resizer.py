"""Image Resizer page for Streamlit app."""

from __future__ import annotations

from io import BytesIO

import streamlit as st

from scrapper.image_resizer import (
    ImageResizerError,
    ResizeOptions,
    load_image_from_bytes,
    load_image_from_url,
    resize_image,
)


def main() -> None:
    st.set_page_config(
        page_title="Image Resizer",
        page_icon="📐",
        layout="wide",
    )

    st.title("📐 Image Resizer")
    st.caption(
        "Resize any image to custom dimensions with optional aspect ratio preservation."
    )

    image_source, settings = render_settings()

    if st.button("Resize Image", type="primary", disabled=not image_source):
        run_resize(image_source, settings)

    render_result()


def render_settings() -> tuple[dict, dict]:
    with st.sidebar:
        st.header("Settings")

        st.subheader("Resize Configuration")
        width = st.number_input(
            "Width (pixels)",
            min_value=1,
            max_value=10000,
            value=800,
            step=1,
        )
        height = st.number_input(
            "Height (pixels)",
            min_value=1,
            max_value=10000,
            value=600,
            step=1,
        )
        maintain_aspect_ratio = st.checkbox(
            "Maintain aspect ratio",
            value=False,
            help="If enabled, the image will fit within the specified dimensions while preserving its original aspect ratio",
        )

        st.divider()
        st.subheader("Quality")
        st.caption("High-quality Lanczos resampling is used automatically.")

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
            help="Enter the URL of the image you want to resize",
        )
        if image_url.strip():
            image_source = {"type": "url", "data": image_url.strip()}

    return image_source, {
        "width": int(width),
        "height": int(height),
        "maintain_aspect_ratio": maintain_aspect_ratio,
    }


def run_resize(image_source: dict, settings: dict) -> None:
    if not image_source:
        st.warning("Please provide an image to resize.")
        return

    try:
        with st.spinner("Loading image..."):
            if image_source["type"] == "file":
                image = load_image_from_bytes(image_source["data"])
            else:
                image = load_image_from_url(image_source["data"])

        with st.spinner("Resizing image..."):
            options = ResizeOptions(**settings)
            result = resize_image(image, options)

    except ImageResizerError as exc:
        st.session_state["resize_error"] = str(exc)
        st.session_state["resize_result"] = None
        return

    st.session_state["resize_result"] = result
    st.session_state["resize_error"] = None


def render_result() -> None:
    error = st.session_state.get("resize_error")
    result = st.session_state.get("resize_result")

    if error:
        st.error(f"Resize failed: {error}")
        return

    if result is None:
        return

    st.divider()
    st.subheader("Resize Result")

    render_metrics(result)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Original Image**")
        st.image(
            result.original_image,
            caption=f"Size: {result.original_size[0]}×{result.original_size[1]} px",
            use_container_width=True,
        )

    with col2:
        st.markdown("**Resized Image**")
        st.image(
            result.resized_image,
            caption=f"Size: {result.new_size[0]}×{result.new_size[1]} px",
            use_container_width=True,
        )

    buf = BytesIO()
    result.resized_image.save(buf, format="PNG")
    buf.seek(0)

    st.download_button(
        "Download Resized Image",
        data=buf,
        file_name="resized_image.png",
        mime="image/png",
    )


def render_metrics(result) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Original Size", f"{result.original_size[0]}×{result.original_size[1]}")
    col2.metric("New Size", f"{result.new_size[0]}×{result.new_size[1]}")

    orig_aspect = result.original_size[0] / result.original_size[1]
    new_aspect = result.new_size[0] / result.new_size[1]
    col3.metric("Original Aspect", f"{orig_aspect:.2f}:1")
    col4.metric("New Aspect", f"{new_aspect:.2f}:1")

    if result.aspect_ratio_maintained:
        st.info("✓ Aspect ratio was preserved during resize")


if __name__ == "__main__":
    main()
