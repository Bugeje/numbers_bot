// src/phaser/scene.js
export class QoderScene extends Phaser.Scene {
  constructor() {
    super('QoderScene');
  }

  preload() {}

  create() {}

  update() {}

  pauseScene() {
    this.scene.pause();
  }

  resumeScene() {
    this.scene.resume();
  }
}