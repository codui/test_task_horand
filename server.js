const express = require("express");
const multer = require("multer");
const cors = require("cors");
const path = require("path");
const fs = require("fs");

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.static("public"));
app.use(express.static("uploads"));

// Функция для создания папки, если её нет
const createFolderIfNotExist = (folderPath) => {
    if (!fs.existsSync(folderPath)) {
        fs.mkdirSync(folderPath, { recursive: true });
    }
};

// Настройка Multer (динамический путь загрузки)
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        const formType = req.headers.formtype; // Читаем заголовок formType
        let folder = "uploads"; // Папка по умолчанию

        if (formType === "A") {
            folder = "uploads/FormA";
        } else if (formType === "B") {
            folder = "uploads/FormB";
        }

        createFolderIfNotExist(folder); // Создаём папку, если её нет
        cb(null, folder);
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + path.extname(file.originalname));
    }
});

const upload = multer({ storage });

app.post("/upload", upload.array("files"), (req, res) => {
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: "Файлы не загружены" });
    }

    res.json({
        message: "Файлы успешно загружены!",
        count: req.files.length,
        folder: req.headers.formtype === "A" ? "FormA" : "FormB"
    });
});

app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(PORT, () => {
    console.log(`Сервер запущен на http://localhost:${PORT}`);
});
