import { application, Router } from 'express';
import path from 'path';
import { dirname } from 'path';
import { fileURLToPath } from 'url';
const router = Router();

// Obtener el directorio actual del archivo
const _dirname = dirname(fileURLToPath(import.meta.url));

import { appendFile } from 'fs';
import fs from 'fs';

// Cuando se solicita una ruta, se responde con el archivo HTML
router.get('/', (req, res) => res.render('index.ejs'));

router.get('/about', (req, res) => res.render('about.ejs'));

router.get('/contact', (req, res) => res.render('contact.ejs'));

export default router;
