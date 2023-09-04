import express from 'express';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { spawn } from 'child_process';

// Crear una instancia de enrutador de Express
const show = express.Router();

const _filename = fileURLToPath(import.meta.url);
const _dirname = dirname(_filename);

// Función para procesar la imagen y renderizar los resultados
function processImageAndRenderResults(req, res, imageName) {
    const uploadsDir = path.join(_dirname, '../public/uploads');

    const imagePath = path.join(uploadsDir, imageName);

    const pythonScriptPath = path.join(_dirname, 'image_processing.py');

    const modelPath = path.join(_dirname, './model.pth');

    // Llamar al script de Python usando child_process.spawn
    const pythonProcess = spawn('python3', [pythonScriptPath, imagePath, modelPath]);
    let image_path = '';
    let postprocessed_image_path = '';

    // Escuchar los datos desde la salida estándar del script
    pythonProcess.stdout.on('data', (data) => {
        const output = data.toString().trim();
        const lines = output.split('\n');
        if (lines.length >= 3) {

            /* LO QUE DEVUELVE EL SCRIPT DE PYTHON:
            print(original_image_name_png)
            print(image_path)
            print(postprocessed_image_path)*/

            image_path = lines[0];
            postprocessed_image_path = lines[2];
        }
    });

    // Escuchar los datos desde la salida de error estándar del script
    pythonProcess.stderr.on('data', (data) => {
        console.error(data.toString().trim());
    });

    // Manejar el cierre del proceso de Python
    pythonProcess.on('close', (code) => {
        console.log('Script de Python finalizado con código', code);
        res.render('results.ejs', { imageName: image_path, postprocessedImagePath: postprocessed_image_path });
    });
}

// Ruta para mostrar los resultados
show.get('/results', (req, res) => {
    const imageName = req.query.fileName;
    processImageAndRenderResults(req, res, imageName);
});

// Exportar el enrutador y la función de procesamiento de imágenes
export { show, processImageAndRenderResults };
