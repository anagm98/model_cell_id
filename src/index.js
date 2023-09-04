// Importar los módulos necesarios
import express from 'express';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import indexRoutes from './routes/index.js';
import upload from './img_scripts/upload.js';
import { show, processImageAndRenderResults } from './img_scripts/show.js';
import session from 'express-session';

// Crear una instancia del servidor Express
const server = express();

// Obtener la ruta absoluta al directorio actual
const _dirname = dirname(fileURLToPath(import.meta.url));

// Configurar el middleware de express-session
server.use(session({
    secret: 'tu-clave-secreta',
    resave: false,
    saveUninitialized: true
}));

server.set('views', join(_dirname, 'views'));

server.use('/results', show);

server.set('view engine', 'ejs');

server.use(indexRoutes);

server.use(express.static(join(_dirname, 'public')));

// Manejar la carga de imágenes usando el middleware 'upload'
server.post('/upload', upload.single('image'), (req, res) => {
    if (!req.file) {
        return res.status(400).send('No hay imágenes cargadas, vuelva atrás');
    }

    const uploadedImgName = req.file.filename;
    req.session.lastUploadedImgName = uploadedImgName;
    processImageAndRenderResults(req, res, uploadedImgName);
});

// Servir imágenes desde el directorio 'uploads'
server.use('/uploads', express.static(join(_dirname, 'public', 'uploads')));

// Manejar la ruta '/results' para mostrar los resultados
server.get('/results', (req, res) => {
    const postprocessedImagePath = req.query.postprocessedImagePath;
    res.render('results.ejs', { postprocessedImagePath });
});

// Iniciar el servidor y escuchar en el puerto 3001
const PUERTO = 3001;
server.listen(PUERTO, () => {
    console.log(`El servidor está escuchando en el puerto ${PUERTO}`);
});
