# Publicar LÚMINA en GitHub

Para que tu profesor pueda revisar el código, crea un repositorio independiente de tus proyectos de trabajo.

## Opción A: Desde VS Code con GitHub CLI (recomendado)

1. Inicia sesión en la cuenta personal de GitHub usando `gh auth login` si todavía no lo has hecho.
2. Abre con **Archivo > Abrir carpeta** esta carpeta del proyecto, no el archivo ZIP.
3. Abre **Terminal > Nueva terminal** y ejecuta en orden:

```powershell
git init
git branch -M main
git add .
git commit -m "Proyecto inicial de LUMINA Algebra Studio"
gh repo create Lumina-Algebra-Studio --public --source=. --remote=origin --push
```

Si Git todavía no conoce tu nombre y correo, configura ambos con `git config --global user.name "Tu nombre"` y `git config --global user.email "tu-email-de-GitHub"`, luego repite el commit.

El repositorio debería quedar accesible en **https://github.com/KarinG-Z/Lumina-Algebra-Studio** cuando lo hayas publicado. La dirección no existirá antes de crear el repositorio.

## Opción B: Desde la web de GitHub

1. Entra a https://github.com/new y crea un repositorio llamado `Lumina-Algebra-Studio`.
2. Elige **Public** para que el profesor pueda consultarlo sin invitación, o **Private** si deseas limitar el acceso (en ese caso deberás invitar al profesor).
3. No agregues README ni `.gitignore` desde GitHub: ambos ya están en la carpeta.
4. Abre la carpeta en VS Code y ejecuta:

```powershell
git init
git branch -M main
git add .
git commit -m "Proyecto inicial de LUMINA Algebra Studio"
git remote add origin https://github.com/KarinG-Z/Lumina-Algebra-Studio.git
git push -u origin main
```

## Para subir futuros cambios

```powershell
git add .
git commit -m "Mejoras de interfaz y calculadora"
git push
```

## ¿Qué adjuntar al profesor?

- Enlace de GitHub al repositorio (si es público).
- Archivo ZIP del proyecto completo, si Classroom permite adjuntos.
- Opcionalmente, dos capturas de los ejercicios resueltos.

Al ejecutar el proyecto, el profesor necesita Python 3.10+ y debe iniciar `INICIAR_LUMINA.bat` (Windows) o `python app.py`.

**Importante:** GitHub Pages no ejecuta Python, por tanto abrir el HTML directamente en Pages no habilitará los cálculos. Para una demostración online habría que desplegar también el servidor Python en un servicio compatible.
