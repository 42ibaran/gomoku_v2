// import logo from './logo.svg';
import './App.css';
import React from 'react';
// import Modal from '@material-ui/core/Modal';
import Grid from '@material-ui/core/Grid';
// import Paper from '@material-ui/core/Paper';
import { Board } from './components/BoardComponent';

// import socketIOClient from "socket.io-client";

// const ENDPOINT = "http://127.0.0.1:5000";

// function App() {
//   // const socket = socketIOClient(ENDPOINT);
//   // socket.emit("connected", {1: 'hello'})
//   // socket.on("update", data => {
//   //   setResponse(data);
//   // });

//   return (
//     <div className="App">
//       <header className="App-header">
//       </header>
//     </div>
//   );
// }


class App extends React.Component {
  // constructor(props) {
  //   super(props)
  //   // this.boardRef = React.createRef()
  // }

  modalClosed = false;

  componentDidMount() {
    // this.myP5 = new p5(this.Sketch, this.boardRef.current);
    // let response = ApiService.post('/init')
    // console.log(response)
  }

  handleClose() {
    this.modalClosed = true
  }

  render() {
    // let board = ""
    // if (this.modalClosed) {
    let board = <Board></Board>
    // }
    return (
      <div className="App">
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Grid container justify="center" spacing={2}>
              {board}
            </Grid>
          </Grid>
        </Grid>
      </div>
      // <div>
      //   <Modal
      //     open={!this.modalClosed}
      //     onClose={this.handleClose}
      //     aria-labelledby="simple-modal-title"
      //     aria-describedby="simple-modal-description"
      //   ></Modal>
      // </div>
    )
  }
}

export default App;
