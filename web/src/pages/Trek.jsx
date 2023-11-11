import { XMLParser } from 'fast-xml-parser';
import React, { Component } from 'react';
import withRouter from '../functions/withRouter';
import { Link } from "react-router-dom";

const VoteOption = ({ option, votes, totalVotes, onVote }) => {
  const percentage = totalVotes ? Math.round((votes / totalVotes) * 100) : 0;

  return (
    <div className='pb-5 '>
      <div className="flex items-stretch">
        <div className="bg-white flex-grow p-3">
          <p className="m-0">{option}</p>
        </div>
        <button
          onClick={() => onVote(option)}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold px-4 self-stretch flex items-center justify-center"
        >
          Vote
        </button>
      </div>
      <div className="w-full text-white bg-gray-200 dark:bg-gray-700 shadow-lg">
        <div
          className="bg-green-600 h-3"
          style={{ width: `${percentage}%` }}>
        </div>
      </div>
    </div>
  );
};

class Trek extends Component {
  constructor(props) {
    super(props);
    this.state = {
      trek: null,
      trekId: this.props.router.params.id,
      downloadedBlobs: {}
    };
    this.addOption = this.addOption.bind(this);
    this.voteForOption = this.voteForOption.bind(this);
  }

  componentDidMount() {
    fetch(`https://texttrek.blob.core.windows.net/treks?restype=container&comp=list&prefix=${this.state.trekId}`)
      .then(res => res.text())
      .then(text => new XMLParser().parse(text).EnumerationResults.Blobs.Blob)
      .then(blobs => {
        if (!blobs) {
          return;
        }
        var blobs = (Array.isArray(blobs) ? blobs : [blobs]).filter(blob => !blob.Name.endsWith("summary.txt") && blob.Name.endsWith(".txt"));
        this.setState({ trek: blobs });
        blobs.map(blob => fetch(blob.Url)
          .then(res => res.text())
          .then(text => this.setState({ [blob.Name]: text })))
      });
    fetch(`https://texttrek.azurewebsites.net/api/get?trek=${this.state.trekId}&code=6-41OE76Gc55lz7CzSvZDbEgl4AZ57NtNTKom0L46EmgAzFuT4Qrbw==`)
      .then(res => res.json())
      .then(votes => this.setState({ votes: votes }));
  }

  addOption() {
    fetch(`https://texttrek.azurewebsites.net/api/add?trek=${this.state.trekId}&code=Tc0wVgJLyF2qWwP_28jQDKmXHweUNmqLPWSWeqDYPk-pAzFumYHhHg==`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ "option": this.state.option })
    })
      .then(res => {
        if (res.status == 200) {
          window.location.reload(false)
        } else {
          res.text().then(text => this.setState({ error: text }))
        }
      });
  }

  voteForOption(option) {
    fetch(`https://texttrek.azurewebsites.net/api/vote?trek=${this.state.trekId}&code=fo3t-iTERsxIBAyW48q90lipinQ52NbfPYThshOdmrTPAzFuA4f8PQ==`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ "option": option })
    })
      .then(res => {
        if (res.status == 200) {
          window.location.reload(false)
        } else {
          res.text().then(text => this.setState({ error: text }))
        }
      });
  }

  getTotalVotes() {
    return;
  }

  render() {
    var totalVotes = this.getTotalVotes();
    return (
      <div className="container mx-auto max-w-4xl my-10">
        <Link to="/">
          <div className="text-center mb-10">
            <img className="mix-blend-darken m-auto invert" width="150px" src="./texttrek.jpg" alt="Text Trek" />
          </div>
        </Link>


        <div className="space-y-5 w-full mb-5">
          {this.state.trek &&
            this.state.trek.map((trek, index) => (
              this.state[trek.Name] ? <div
                className={`flex flex-col space-y-3 p-5 bg-white shadow-lg`}
                key={trek.Name}
              >
                <img className="m-auto" src={trek.Url.replace(".txt", ".png")} alt="" />
                {this.state[trek.Name].split('\n').map((p, i) => (
                  <p className="text-gray-700 text-lg leading-relaxed" key={i}>{p}</p>
                ))}
              </div> : <></>
            ))}
        </div>

        {Array.isArray(this.state.votes) && this.state.votes.map((v) => (
          <VoteOption
            key={v.option}
            option={v.option}
            votes={v.votes}
            totalVotes={Math.max(...this.state.votes.map(x => x.votes))}
            onVote={this.voteForOption}
          />
        ))}

        {this.state.error ?
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 mb-5 relative shadow-lg" role="alert">
            <span className="block sm:inline">{this.state.error}</span>
            <span className="absolute top-0 bottom-0 right-0 px-4 py-3" onClick={() => this.setState({ error: null })}>
              <svg className="fill-current h-6 w-6 text-red-500" role="button" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><title>Close</title><path d="M14.348 14.849a1.2 1.2 0 0 1-1.697 0L10 11.819l-2.651 3.029a1.2 1.2 0 1 1-1.697-1.697l2.758-3.15-2.759-3.152a1.2 1.2 0 1 1 1.697-1.697L10 8.183l2.651-3.031a1.2 1.2 0 1 1 1.697 1.697l-2.758 3.152 2.758 3.15a1.2 1.2 0 0 1 0 1.698z" /></svg>
            </span>
          </div> : <></>}

        <div className="flex shadow-lg">
          <input
            className="flex-grow p-2 border border-r-0 border-gray-300"
            type="text"
            placeholder="Suggest a new option..."
            onChange={(ev) => this.setState({ option: ev.currentTarget.value })}
          />
          <button
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 focus:outline-none focus:shadow-outline"
            onClick={this.addOption}
          >
            Add
          </button>
        </div>
      </div>
    );
  }
}

export default withRouter(Trek);