"""Image Generation page for Streamlit app."""

from __future__ import annotations

from io import BytesIO

import streamlit as st

from scrapper.image_generator import (
    ImageGenerationError,
    ImageGenerationOptions,
    generate_images,
)


def main() -> None:
    st.set_page_config(
        page_title="Image Generation",
        page_icon="🎨",
        layout="wide",
    )

    st.title("🎨 AI Image Generation")
    st.caption(
        "Generate images using AI models. Enter a prompt and customize your image settings."
    )

    prompt, settings = render_settings()

    starter_prompt = st.session_state.get("starter_prompt", "")

    if st.button("Generate Images", type="primary", disabled=not prompt):
        run_generation(prompt, settings, starter_prompt)

    render_result()

    st.caption(
        "Images are generated using OpenAI-compatible API. "
        "Make sure your API_URL and API_KEY are configured in the .env file."
    )


def render_settings() -> tuple[str, dict]:
    with st.sidebar:
        st.header("Settings")

        st.subheader("Model")
        model = st.radio(
            "Choose model",
            options=["claude-sonnet-4-6", "claude-haiku-4-5-20251001"],
            index=0,
            help="Select the AI model for image generation",
        )

        st.divider()
        st.subheader("Image Configuration")



        st.divider()
        st.subheader("Advanced")
        st.caption("API timeout and retries are handled automatically.")

    if "starter_prompt" not in st.session_state:
        st.session_state.starter_prompt = ""

    starter_prompt = st.text_input(
        "Starter prompt (optional)",
        value=st.session_state.starter_prompt,
        placeholder="e.g., Create a photorealistic image of...",
        help="A prefix that will be automatically added to your main prompt",
    )

    if starter_prompt != st.session_state.starter_prompt:
        st.session_state.starter_prompt = starter_prompt

    prompt = st.text_area(
        "Image prompt",
        placeholder="A serene landscape with mountains and a lake at sunset...",
        height=100,
        help="Describe the image you want to generate",
    )

    return prompt, {
        "model": model
    }


def run_generation(prompt: str, settings: dict, starter_prompt: str = "") -> None:
    if not prompt.strip():
        st.warning("Please enter a prompt to generate images.")
        return

    combined_prompt = prompt.strip()
    if starter_prompt.strip():
        combined_prompt = f"{starter_prompt.strip()} {combined_prompt}"

    options = ImageGenerationOptions(prompt=combined_prompt, **settings)

    try:
        with st.spinner(f"Generating image(s)..."):
            results = generate_images(options)
    except ImageGenerationError as exc:
        st.session_state["generation_error"] = str(exc)
        st.session_state["generation_results"] = None
        return

    st.session_state["generation_results"] = results
    st.session_state["generation_error"] = None


def render_result() -> None:
    error = st.session_state.get("generation_error")
    results = st.session_state.get("generation_results")

    if error:
        st.error(f"Generation failed: {error}")
        return

    if results is None:
        return

    st.divider()
    st.subheader(f"Generated {len(results)} image(s)")

    for idx, result in enumerate(results, start=1):
        render_metrics(result, idx)

        st.image(
            result.image,
            caption=f"Prompt: {result.prompt}",
            use_container_width=True,
        )

        if result.revised_prompt and result.revised_prompt != result.prompt:
            with st.expander("View revised prompt"):
                st.caption(
                    "The AI model may revise your prompt for better results or safety."
                )
                st.text(result.revised_prompt)

        buf = BytesIO()
        result.image.save(buf, format="PNG")
        buf.seek(0)

        st.download_button(
            f"Download image {idx}",
            data=buf,
            file_name=f"generated_image_{idx}.png",
            mime="image/png",
        )

        if idx < len(results):
            st.divider()


def render_metrics(result, idx: int) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Image", f"#{idx}")
    col2.metric("Model", result.model)
    col3.metric("Size", result.size)
    col4.metric("Dimensions", f"{result.image.width}×{result.image.height} px")


if __name__ == "__main__":
    main()
