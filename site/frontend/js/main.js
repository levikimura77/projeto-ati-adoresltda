const form = document.querySelector("#suggestion-form");
const statusBox = document.querySelector("#form-status");

if (form && statusBox) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const submitButton = form.querySelector('button[type="submit"]');
    const originalLabel = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.textContent = "Salvando...";
    statusBox.hidden = false;
    statusBox.classList.remove("is-error");
    statusBox.textContent = "Enviando sua ideia para a equipe...";

    const payload = Object.fromEntries(new FormData(form).entries());

    try {
      const response = await fetch(form.action, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const contentType = response.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) {
        throw new Error("Para salvar sugestões, inicie o servidor Python e abra http://127.0.0.1:5000.");
      }
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Não foi possível salvar sua sugestão.");
      }

      statusBox.textContent = "Sugestão recebida! Obrigado por ajudar a construir os próximos capítulos.";
      form.reset();
    } catch (error) {
      statusBox.classList.add("is-error");
      statusBox.textContent = error instanceof TypeError
        ? "Não foi possível conectar ao servidor. Tente novamente em instantes."
        : error.message;
    } finally {
      submitButton.disabled = false;
      submitButton.innerHTML = originalLabel;
    }
  });
}
