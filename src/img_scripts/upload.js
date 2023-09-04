import multer from 'multer';
import path from 'path';
import { dirname } from 'path';

// Ruta del directorio actual del archivo
const _dirname = path.dirname(new URL(import.meta.url).pathname);

// Configuración de Multer para subir imágenes con cualquier extensión
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const destinationPath = path.resolve(_dirname, '../public/uploads');
        cb(null, destinationPath);
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        const originalExtension = path.extname(file.originalname);
        cb(null, file.fieldname + '-' + uniqueSuffix + originalExtension);
    }
});

// Crear una instancia de Multer con la configuración de almacenamiento y exportarla
const upload = multer({ storage: storage });

export default upload;
