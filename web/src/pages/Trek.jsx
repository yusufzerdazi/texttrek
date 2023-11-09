import { XMLParser } from 'fast-xml-parser';
import React, { Component } from 'react';
import withRouter from '../functions/withRouter';
import { Link } from "react-router-dom";

class Trek extends Component {
    constructor(props){
      super(props);
      this.state = {
        trek: null,
        trekId: this.props.router.params.id,
        downloadedBlobs: {}
      };
      this.addOption = this.addOption.bind(this);
      this.voteForOption = this.voteForOption.bind(this);
    }
  
    componentDidMount(){
      fetch(`https://texttrek.blob.core.windows.net/treks?restype=container&comp=list&prefix=${this.state.trekId}`)
        .then(res => res.text())
        .then(text => new XMLParser().parse(text).EnumerationResults.Blobs.Blob)
        .then(blobs => {
          if(!blobs) {
            return;
          }
          this.setState({trek: Array.isArray(blobs) ? blobs : [blobs]});
          blobs.filter(blob => !blob.Name.endsWith("summary.txt") && blob.Name.endsWith(".txt")).map(blob => fetch(blob.Url)
            .then(res => res.text())
            .then(text => this.setState({[blob.Name]: text})))
        });
      fetch(`https://texttrek.azurewebsites.net/api/get?trek=${this.state.trekId}&code=6-41OE76Gc55lz7CzSvZDbEgl4AZ57NtNTKom0L46EmgAzFuT4Qrbw==`)
        .then(res => res.json())
        .then(votes => this.setState({votes: votes}));
    }

    addOption() {
      fetch(`https://texttrek.azurewebsites.net/api/add?trek=${this.state.trekId}&code=Tc0wVgJLyF2qWwP_28jQDKmXHweUNmqLPWSWeqDYPk-pAzFumYHhHg==`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({"option": this.state.option})
      })
      .then(res => {
        if(res.status == 200){
          window.location.reload(false)
        } else {
          res.text().then(text => this.setState({error: text}))
        }
      });
    }

    voteForOption(option){
      fetch(`https://texttrek.azurewebsites.net/api/vote?trek=${this.state.trekId}&code=fo3t-iTERsxIBAyW48q90lipinQ52NbfPYThshOdmrTPAzFuA4f8PQ==`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({"option": option})
      })
      .then(res => {
        if(res.status == 200){
          window.location.reload(false)
        } else {
          res.text().then(text => this.setState({error: text}))
        }
      });
    }
  
    render() {
      return <div className="container mx-auto items-center max-w-4xl pb-5" >
        <Link to="/">
          <h1 className="text-3xl font-bold text-center p-5 pb-0">
            <img className="mix-blend-darken m-auto invert" width="150px" src="./texttrek.jpg"></img>
          </h1>
        </Link>
        <div className='mb-5'>
        { this.state.trek ? this.state.trek.map(trek => {
          if(trek.Name.endsWith(".png")){
            return <div className="p-5">
              <img key={trek.Name} width="100%" className='m-auto shadow-xl rounded-2xl max-w-md' src={trek.Url}></img>
            </div>
          } else {
            return this.state[trek.Name] ? <div className='shadow-xl bg-white p-5 rounded-2xl' key={trek.Name}>{this.state[trek.Name].split("\n").map(
              (p, i) => <p key={i} className='italic indent-4 '>{p}</p>
            )}</div> : <></>
          }
        }) : <></> }
        </div>
        {Array.isArray(this.state.votes) ? this.state.votes.map(v => 

        <div className='grid grid-cols-6 gap-0 pb-5'>
          <div className='shadow-xl italic bg-teal-100 p-5 rounded-l-2xl col-span-4'>{v.option}</div>
          <div className='shadow-xl text-center bg-green-200 p-5 col-span-1'><b>Votes: </b>{v.votes}</div>
          <button className="shadow-xl btn btn-blue col-span-1" onClick={() => this.voteForOption(v.option)}>Vote</button>
        </div>
        ) : <></>}
        { this.state.error ?
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mb-5 rounded relative" role="alert">
          <span className="block sm:inline">{this.state.error}</span>
          <span className="absolute top-0 bottom-0 right-0 px-4 py-3" onClick={() => this.setState({error: null})}>
            <svg className="fill-current h-6 w-6 text-red-500" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><title>Close</title><path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z"/></svg>
          </span>
        </div> : <></> }
        <div className='grid grid-cols-6 gap-0'>
          <input placeholder='What do you do?' className='col-span-5 italic shadow-xl rounded-l-2xl border-0' type="text" onChange={ev => this.setState({option: ev.currentTarget.value})}></input>
          <button className="shadow-xl btn btn-blue col-span-1" onClick={this.addOption}>Add</button>
        </div>
      </div>
    }
}
  
export default withRouter(Trek);
