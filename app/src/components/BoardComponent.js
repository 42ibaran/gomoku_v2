import React from 'react';
import {ApiService} from '../services/ApiService'

const p5 = require('p5')

const EMPTY = 0
const WHITE = 1
const BLACK = 2
const WHITE_M = 255
const BLACK_M = 0
const WHITE_S = 128
const BLACK_S = 128

const COLOR_CODES = {
  1: {
    'move': WHITE_M,
    'suggestion': WHITE_S,
  },
  2: {
    'move': BLACK_M,
    'suggestion': BLACK_S,
  },
}

var is_over = false
var move = BLACK
var previous_board = null

export class Board extends React.Component {

  constructor(props) {
    super(props)
    this.boardRef = React.createRef()
  }

  componentDidMount() {
    this.myP5 = new p5(this.Sketch, this.boardRef.current);
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

    p.setup = async () => {
      await ApiService.post('/init').then(response => {
        if (response['move']) {
          move = WHITE
        }
        previous_board = response['board']
      })
      cnv = p.createCanvas(dim, dim);
      cnv.mouseClicked(click);

      p.render_board(previous_board)
      p.noLoop()
    }

    p.drawCircle = (x, y, color) => {
      let posX = (x + 1) * offset
      let posY = (y + 1) * offset
    
      let c = p.color(color, color, color, 255)
      p.fill(c);
      p.circle(posX, posY, offset - 1);
    }

    p.render_board = (board) => {
      p.clear()
      p.background(200, 200, 200, 150);
      let c = p.color(0, 0, 0, 255)
      p.stroke(c)

      for (let pos = 0; pos < size; pos++) {
          let finalPos = offset + offset * pos;
          p.line(finalPos, offset / 2, finalPos, dim - offset / 2);
          p.line(offset / 2, finalPos, dim - offset / 2, finalPos);
      }

      if (!board) {
        return
      }
      for (let y = 0; y < size; y++) {
        for (let x = 0; x < size; x++) {
          let value = board[y][x]
          if (value !== EMPTY) {
            p.drawCircle(x, y, COLOR_CODES[value]['move'])
          }
        }
      }
    }

    function click() {
      if (is_over) {
        alert("The game is already over. Take a break.")
        return
      }
      let x = Math.round((p.mouseX - 20) / offset)
      let y = Math.round((p.mouseY - 20) / offset)

      if (y < 0 || y > 18 || x < 0 || x > 18) {
        return
      }

      p.drawCircle(x, y, COLOR_CODES[move]['move'])
      
      ApiService.post('/make-move', {
        color: move,
        position: [y, x]
      }).then(data => {
        if (!data['board']) {
          p.render_board(previous_board)
          alert(data['message'])
          return
        }
        console.log("Time move: ", data['time_move'] ?? "-")
        console.log("Time suggestion: ", data['time_suggestion'] ?? '-')
        is_over = data['is_over']
        p.render_board(data['board'])
        if (data['move']) {
        } else {
          move = move === BLACK ? WHITE : BLACK
        }
        if (data['suggestion']) {
          let color = data['suggestion']['color']
          let y_sugg = data['suggestion']['position'][0]
          let x_sugg = data['suggestion']['position'][1]
          p.drawCircle(x_sugg, y_sugg, COLOR_CODES[color]['suggestion'])
        }
        previous_board = data['board']
      })
    }
  }
}