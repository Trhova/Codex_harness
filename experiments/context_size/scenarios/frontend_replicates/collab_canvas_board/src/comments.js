export function renderComments(host, comments) {
  host.innerHTML = `
    <h1>Comments</h1>
    ${comments
      .map(
        (comment) => `
          <article>
            <strong>${comment.author}</strong>
            <p>${comment.text}</p>
            <span>${comment.shapeId}</span>
          </article>
        `
      )
      .join("")}
  `;
}
