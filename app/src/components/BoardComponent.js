import React from 'react';
import {ApiService} from '../services/ApiService'
const p5 = require('p5')

const EMPTY = 0
const WHITE = 1
const BLACK = 2
const WHITE_M = 255
const BLACK_M = 0
const WHITE_S = 192
const BLACK_S = 64

var move = BLACK
var previous_board = null

export class Board extends React.Component {
  constructor(props) {
    super(props)
    this.boardRef = React.createRef()
  }

  componentDidMount() {
    this.myP5 = new p5(this.Sketch, this.boardRef.current);
    let response = ApiService.post('/init')
    if (response['move']) {
      move = WHITE
    }
    previous_board = response['board']
  }

  render() {
    return (
      <div ref={this.boardRef}>
      </div>
    )
  }

  Sketch = (p) => {
    let cnv

    const dim = 700
    const size = 19
    const offset = dim / (size + 1)

    p.setup = () => {
      cnv = p.createCanvas(dim, dim);
      cnv.mouseClicked(click);

      let c = p.color(0, 0, 0, 255)
      p.stroke(c)

      for (let pos = 0; pos < size; pos++) {
          let finalPos = offset + offset * pos;
          p.line(finalPos, offset / 2, finalPos, dim - offset / 2);
          p.line(offset / 2, finalPos, dim - offset / 2, finalPos);
      }
      
      p.noLoop()
    }

    p.drawCircle = (x, y, color) => {
      let posX = (x + 1) * offset
      let posY = (y + 1) * offset
    
      let c = p.color(color, color, color, 255)
      p.fill(c);
      p.circle(posX, posY, offset - 1);
    }

    function render_board(board) {
      p.setup()
      if (!board) {
        return
      }
      for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
          let value = board[y][x]
          if (value !== EMPTY) {
            let color = value === WHITE ? WHITE_M : BLACK_M
            p.drawCircle(x, y, color)
          }
        }
      }
    }

    function click() {
      let x = Math.round((p.mouseX - 20) / offset)
      let y = Math.round((p.mouseY - 20) / offset)

      p.drawCircle(x, y, move)
      move = move === BLACK ? WHITE : BLACK

      ApiService.post('/make-move', {
        color: move,
        position: [y, x]
      }).then(data => {
        if (data['board'] === undefined) {
          render_board(previous_board)
          return
        }
        render_board(data['board'])
        if (data['move']) {
          move = data['move']['color'] === BLACK ? WHITE : BLACK
        }
        if (data['suggestion']) {
          let color = data['suggestion']['color'] === WHITE ? WHITE_S : BLACK_S
          let y_sugg = data['suggestion']['position'][0]
          let x_sugg = data['suggestion']['position'][1]
          p.drawCircle(x_sugg, y_sugg, color)
        }
        previous_board = data['board']
      })
    }
  }
}