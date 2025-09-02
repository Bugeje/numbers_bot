// src/phaser/game.js
import { QoderScene } from './scene.js';

let game = null;

export function mountPhaser(parentId = 'phaser-container') {
  const parent = document.getElementById(parentId);
  if (!parent) return null;

  const config = {
    type: Phaser.AUTO,
    backgroundColor: '#1a1b1e',
    parent: parentId,
    scale: {
      mode: Phaser.Scale.RESIZE,
      autoCenter: Phaser.Scale.CENTER_BOTH,
      width: parent.clientWidth || 600,
      height: parent.clientHeight || 360
    },
    scene: [QoderScene]
  };

  game = new Phaser.Game(config);
  return game;
}

export function pausePhaser() {
  if (!game) return;
  const scene = game.scene.getScene('QoderScene');
  scene?.pauseScene?.();
}

export function resumePhaser() {
  if (!game) return;
  const scene = game.scene.getScene('QoderScene');
  scene?.resumeScene?.();
}

export function destroyPhaser() {
  game?.destroy(true);
  game = null;
}