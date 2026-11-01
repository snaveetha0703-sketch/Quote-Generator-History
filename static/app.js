
let currentQuote = "";
let currentAuthor = "";


// Get a random quote
async function getQuote() {

    const quoteElement = document.getElementById("quote");
    quoteElement.textContent = "Loading...";

    try {
        const response = await fetch("/api/quote");

        if (!response.ok) {
            throw new Error("Unable to get quote");
        }

        const data = await response.json();

        currentQuote = data.quote;
        currentAuthor = data.author;

        quoteElement.textContent = currentQuote;

        document.getElementById("author").textContent =
            "- " + currentAuthor;

        document.getElementById("source").textContent =
            "Source: " + data.source;

    } catch (error) {
        quoteElement.textContent = "Unable to load quote.";
    }
}


// Save favorite quote
async function saveFavorite() {

    if (!currentQuote) {
        alert("Please load a quote first!");
        return;
    }

    const response = await fetch("/api/favorites", {
        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            quote: currentQuote,
            author: currentAuthor
        })
    });

    const data = await response.json();

    document.getElementById("message").textContent =
        data.message || data.error;

    if (response.ok) {
        loadFavorites();
    }
}


// Display favorite history
async function loadFavorites() {

    const response = await fetch("/api/favorites");
    const data = await response.json();

    const list = document.getElementById("favorites");

    list.innerHTML = "";

    if (data.length === 0) {
        list.textContent = "No favorite quotes saved yet.";
        return;
    }

    data.forEach(item => {

        const card = document.createElement("div");
        card.className = "favorite-item";

        const quote = document.createElement("p");
        quote.textContent = '"' + item.quote + '"';

        const author = document.createElement("strong");
        author.textContent = "- " + item.author;

        const copyButton = document.createElement("button");
        copyButton.textContent = "Copy";

        copyButton.onclick = () => {
            copyText(item.quote + " - " + item.author);
        };

        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";

        deleteButton.onclick = () => {
            deleteFavorite(item.id);
        };

        card.append(quote, author, document.createElement("br"),
                    copyButton, deleteButton);

        list.appendChild(card);

    });
}


// Copy current quote
async function copyQuote() {

    if (!currentQuote) {
        alert("Please load a quote first!");
        return;
    }

    await copyText(currentQuote + " - " + currentAuthor);
}


// Copy text to clipboard
async function copyText(text) {

    try {
        await navigator.clipboard.writeText(text);
        alert("Quote copied successfully!");
    } catch (error) {
        alert("Copy failed. Please use localhost or HTTPS.");
    }
}


// Delete favorite quote
async function deleteFavorite(id) {

    const response = await fetch("/api/favorites/" + id, {
        method: "DELETE"
    });

    if (response.ok) {
        loadFavorites();
    }
}


// Load application
getQuote();
loadFavorites();
