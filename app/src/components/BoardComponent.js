import React from 'react';
import {ApiService} from '../services/ApiService'
const p5 = require('p5')

export class Board extends React.Component {
  constructor(props) {
    super(props)
    this.boardRef = React.createRef()
  }

  componentDidMount() {
    this.myP5 = new p5(this.Sketch, this.boardRef.current);
    let response = ApiService.post('/init')
    console.log(response)
  }

  render() {
    return (
      <div ref={this.boardRef}>
      </div>
    )
  }

  Sketch = (p) => {
    let cnv
    // let white = 0

    const dim = 400
    const size = 10
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

    p.drawCircle = (x, y, white) => {
      let posX = (x + 1) * offset
      let posY = (y + 1) * offset
    
      let c = p.color(255 * white, 255 * white, 255 * white, 255)
      p.fill(c);
      p.circle(posX, posY, offset - 1);
    }

    function click() {
      let x = Math.round((p.mouseX - 20) / offset)
      let y = Math.round((p.mouseY - 20) / offset)

      ApiService.post('/check-move', {
        position : [y, x]
      }).then(data => {
        if (data.allowed === true) {
          p.drawCircle(x, y, 0)
          ApiService.post('/make-move', {
            position : [y, x]
          }).then(data => {
            if (data['ai_move']) {
              y = data['ai_move'][0]
              x = data['ai_move'][1]
              p.drawCircle(x, y, 1)
            }
          })
        }
      })
    }
  }
}


