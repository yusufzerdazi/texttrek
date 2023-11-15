import { XMLParser } from 'fast-xml-parser';
import React, { Component } from 'react';
import withRouter from '../functions/withRouter';

class StoryV1 extends Component {
    constructor(props) {
        super(props);
        console.log(props)
        this.state = {
            trek: null,
            trekId: this.props.trekId,
            downloadedBlobs: {}
        };
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
    }

    render() {
        return (
            <div className="space-y-5 w-full mb-5">
                {this.state.trek && this.state.trek.map((trek, index) => (
                    this.state[trek.Name] ? <div className={`flex flex-col space-y-3 p-5 bg-white shadow-lg`} key={"" + index}>
                        <img className="m-auto" src={trek.Url.replace(".txt", ".png")} alt="" />
                        <div>
                        {this.state[trek.Name].split('\n').map((p, i) => (
                            <p className="text-gray-700 text-lg leading-relaxed" key={"" + i}>{p}</p>
                        ))}
                        </div>
                    </div> : <></>
                ))}
            </div>
        );
    }
}

export default withRouter(StoryV1);