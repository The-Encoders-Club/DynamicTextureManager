# Dynamic Texture Manager (DTM)

Forget about overwriting original game assets and constantly restarting your game! This submod for **Monika After Story** introduces a real-time, dynamic texture management and loading system.

Unlike the traditional method that requires replacing the base assets of MAS, this submod acts as a **texture framework**: it creates a dedicated folder structure where you can drop custom texture packs, allowing you to alternate between different visual styles and interfaces instantly, right from inside the game.

> [!WARNING]
> This submod is a **technical tool / framework**. It does NOT include textures, backgrounds, or visual elements out of the box. All custom packs are created and provided by you or the community.

## ✨ Key Features

* **Hot-Swapping:** Change the visual look of your game instantly. No need to close and reopen MAS every time you want to try a new style.
* **Smart Persistence:** The submod tracks your active selections automatically. Your preferences remain perfectly saved even after restarting MAS or updating the game.
* **Clean Organization:** Organize your textures by categories using custom folders instead of cluttering or messing with Ren'Py base files.
* **Performance Optimization:** Built to be extremely lightweight and stable, ensuring smooth texture switching without causing lag or memory leaks during long gameplay sessions.

## 🛠️ Installation Guide

Follow these simple steps to get the submod running:

1. **Download:** Go to the **Releases** section on the right side of this repository and download the latest `.zip` file.
2. **Extract:** Extract the contents. You will get a folder named `DynamicTextureManager`.
3. **Install:** Copy the entire `DynamicTextureManager` folder and paste it into your MAS directory under:
   `game/submods/`
4. **First Launch:** Run your game once. The submod will automatically generate the required `textures/` directory at your game's root folder, alongside the `config.json` file.
5. **Add Your Textures:** Close the game, navigate into the newly generated `textures/` folder at the root level, and drop your community texture packs into their corresponding categories!

## 📂 Folder Structure

This is how the submod files and asset folders are organized within your game directory:

```text
MAS_Root_Directory/
├── game/
│   └── submods/
│       └── DTM/
│           ├── header.rpy       <-- Submod registration
│           └── dtm.rpy          <-- Core logic (File scanning & runtime swapping)
└── textures/                    <-- Main assets folder (Auto-generated at the root)
    ├── config.json              <-- Auto-generated (Maintains persistence after restart)
    ├── games/
    │   ├── chess/               └── [Your_Pack_Folder]/ -> (Only .png files inside)
    │   ├── nou/                 └── [Your_Pack_Folder]/
    │   └── pong/                └── [Your_Pack_Folder]/
    └── monika/
        ├── body/                └── [Your_Pack_Folder]/
        ├── ears/                └── [Your_Pack_Folder]/
        ├── eyes/                └── [Your_Pack_Folder]/
        ├── mouth/               └── [Your_Pack_Folder]/
        └── nose/                └── [Your_Pack_Folder]/
```

## 📖 How to Use

Using the framework to add and swap custom textures is incredibly simple for both users and content creators. Follow these steps:

### 1. Create a Texture Pack Folder
Navigate to the specific category you want to modify inside the root `textures/` folder and create a new folder. You can name this folder anything you like (this name will show up in the in-game menu).
* **Example:** To add custom eyes, go to `textures/monika/eyes/` and create a folder named `Anime_Style_Eyes`.

### 2. Add Your Images
Drop your custom `.png` files directly inside your newly created folder.

> [!IMPORTANT]
> The folder must only contain image files, and the filenames must match the original game asset names exactly so the loader can map them correctly.

### 3. Change Textures In-Game
1. Launch MAS and click on **Talk** → **Hey, Monika...** → **Appearance** → **"I want to change the textures"**.
2. A custom menu will appear listing all the folders you created.
3. Select your pack, and the textures will update instantly on your screen without requiring a restart!

Your choice will be automatically saved to `config.json`, keeping your custom look active every time you open the game.
