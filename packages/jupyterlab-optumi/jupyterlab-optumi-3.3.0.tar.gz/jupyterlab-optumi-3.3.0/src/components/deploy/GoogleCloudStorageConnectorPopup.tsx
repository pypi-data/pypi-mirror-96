/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import { Button, CircularProgress, Dialog, DialogContent, /*IconButton,*/ withStyles } from '@material-ui/core';
import { CSSProperties } from '@material-ui/core/styles/withStyles';
import { ArrowBackIos } from '@material-ui/icons';
import * as React from 'react'
import { Global } from '../../Global';
import MuiDialogTitle from '@material-ui/core/DialogTitle';
import { ShadowedDivider, TextBox } from '../../core';

import { ServerConnection } from '@jupyterlab/services';
import { CreateDataConnector } from './CreateDataConnector';
import { DataService } from './dataConnectorBrowser/DataConnectorDirListingItemIcon';
import { OptumiMetadataTracker } from '../../models/OptumiMetadataTracker';
import { NotebookPanel } from '@jupyterlab/notebook';
import { DataConnectorUploadMetadata } from '../../models/DataConnectorUploadMetadata';
import { UploadMetadata } from '../../models/UploadMetadata';

const StyledDialog = withStyles({
    paper: {
        width: 'calc(min(80%, 600px + 150px + 2px))',
        // width: '100%',
        height: '80%',
        overflowY: 'visible',
        backgroundColor: 'var(--jp-layout-color1)',
        maxWidth: 'inherit',
    },
})(Dialog);

const StyledButton = withStyles({
    startIcon: {
        marginRight: '0px',
    },
    iconSizeMedium: {
        '& > *:first-child': {
            fontSize: '12px',
        },
    }
 })(Button);

interface IProps {
    handleClose?: () => any
    style?: CSSProperties
}

interface IState {
    open: boolean
    name: string
    bucketName: string
    serviceAccountKey: string
    waiting: boolean
    spinning: boolean
    errorMessage: string
}

const LABEL_WIDTH = '136px'

export class GoogleCloudStorageConnectorPopup extends React.Component<IProps, IState> {

    constructor(props: IProps) {
        super(props);
		this.state = {
            open: false,
            name: '',
            bucketName: '',
            serviceAccountKey: '',
            waiting: false,
            spinning: false,
            errorMessage: '',
		};
    }
    
    private handleClickOpen = () => {
		this.setState({ open: true });
	}

	private handleClose = () => {
        if (!this.state.waiting) {
            if (this.props.handleClose) this.props.handleClose();
            this.setState({
                open: false,
                name: '',
                bucketName: '',
                serviceAccountKey: '',
                waiting: false,
                spinning: false,
                errorMessage: '',
            });
        }
    }
    
    private nameHasError = (name: string): boolean => {
        const tracker: OptumiMetadataTracker = Global.metadata;
        const optumi = tracker.getMetadata();
        const upload: UploadMetadata = optumi.metadata.upload;
        const dataConnectors = upload.dataConnectors;
        for (var i = 0; i < dataConnectors.length; i++) {
            if (dataConnectors[i].name === name) return true;
        }
        return false;
    }

    private handleCreate = (add?: boolean) => {
        this.setState({ waiting: true, spinning: false })
        setTimeout(() => this.setState({ spinning: true }), 1000)
        const settings = ServerConnection.makeSettings();
		const url = settings.baseUrl + "optumi/add-data-connector";
		const init: RequestInit = {
			method: 'POST',
			body: JSON.stringify({
                // TODO:JJ Change this once we support multiple data connector types
                dataService: DataService.GOOGLE_CLOUD_STORAGE,
                name: this.state.name,
                info: JSON.stringify({
                    bucketName: this.state.bucketName,
                    serviceAccountKey: this.state.serviceAccountKey,
                }),
			}),
		};
		ServerConnection.makeRequest(
			url,
			init, 
			settings
            ).then((response: Response) => {
                Global.handleResponse(response);
            }).then(() => {
                this.setState({ waiting: false, spinning: false})
                if (add && !this.nameHasError(this.state.name)) {
                    const tracker = Global.metadata
                    const optumi = tracker.getMetadata()
                    var dataConnectors = optumi.metadata.upload.dataConnectors
                    dataConnectors.push(new DataConnectorUploadMetadata({
                        name: this.state.name,
                        dataService: DataService.GOOGLE_CLOUD_STORAGE,
                    }))
                    tracker.setMetadata(optumi)
                }
                // Success
                this.handleClose()
            }, (error: ServerConnection.ResponseError) => {
                error.response.text().then((text: string) => {
                    // Show what went wrong
                    this.setState({ waiting: false, spinning: false, errorMessage: text });
                });
            });
    }

    private handleKeyDown = (event: KeyboardEvent) => {
        if (!this.state.open) return;
        if (event.key === 'Enter') this.handleCreate();
        if (event.key === 'Escape') this.handleClose();
    }

    public render = (): JSX.Element => {
        if (Global.shouldLogOnRender) console.log('GoogleCloudStorageConnectorPopupRender (' + new Date().getSeconds() + ')');
        return (
            <div style={Object.assign({}, this.props.style)} >
                <CreateDataConnector
                    iconClass='jp-cloud-logo'
                    dataService={DataService.GOOGLE_CLOUD_STORAGE}
                    description='Access a Cloud Storage bucket'
                    handleClick={this.handleClickOpen}
                />
                <StyledDialog
                    disableBackdropClick
					open={this.state.open}
					onClose={this.handleClose}
                    scroll='paper'
				>
					<MuiDialogTitle
					    disableTypography
                        style={{
                            display: 'inline-flex',
                            backgroundColor: 'var(--jp-layout-color2)',
                            height: '60px',
                            padding: '6px',
                            borderRadius: '4px',
                        }}
                    >
                        <div style={{
                            display: 'inline-flex',
                            flexGrow: 1,
                            marginLeft: '-6px', // this is to counteract the padding in CreateDataConnector so we can reuse it without messing with it
                        }}>
                            <CreateDataConnector
                                iconClass='jp-cloud-logo'
                                dataService={DataService.GOOGLE_CLOUD_STORAGE}
                                style={{zoom: 1.5}}
                            />
                        </div>
                        <div>
                            <StyledButton
                                disableElevation
                                style={{ margin: '6px', height: '36px' }}
                                variant='outlined'
                                onClick={this.handleClose}
                                disabled={this.state.waiting}
                                startIcon={<ArrowBackIos />}
                            >
                                Back
                            </StyledButton>
                        </div>
                        <div>
                            <Button
                                disableElevation
                                style={{ margin: '6px', height: '36px' }}
                                variant='contained'
                                color='primary'
                                onClick={() => this.handleCreate(false)}
                                disabled={this.state.waiting}
                            >
                                {this.state.waiting && this.state.spinning ? <CircularProgress size='1.75em'/> : 'Create'}
                            </Button>
                            <Button
                                disableElevation
                                style={{ margin: '6px', height: '36px' }}
                                variant='contained'
                                color='primary'
                                onClick={() => this.handleCreate(true)}
                                disabled={(!(Global.labShell.currentWidget instanceof NotebookPanel) && Global.tracker.currentWidget != null) || this.state.waiting}
                            >
                                {this.state.waiting && this.state.spinning ? <CircularProgress size='1.75em'/> : 'Create and add to notebook'}
                            </Button>
                        </div>
					</MuiDialogTitle>
                    <ShadowedDivider />
                    <DialogContent style={{padding: '0px'}}>
                        <div style={{padding: '12px'}}>
                            <div style={{margin: '12px 18px 18px 18px'}}>
                                Connect to a Google Cloud Storage bucket using a Service Account.
                            </div>
                            <TextBox<string>
                                getValue={() => this.state.name}
                                saveValue={(value: string) => this.setState({ name: value })}
                                label='Connector Name'
                                helperText="We will create a directory with this name. You can access your data through the path ‘~/data/connector_name/’."
                                labelWidth={LABEL_WIDTH}
                                disabledMessage={this.state.waiting ? "We will create a directory with this name. You can access your data through the path ‘~/data/connector_name/’." : ''}
                                required
                            />
                            <TextBox<string>
                                getValue={() => this.state.bucketName}
                                saveValue={(value: string) => this.setState({ bucketName: value })}
                                label='Bucket Name'
                                helperText='The Bucket Name as specified in Google Cloud Storage documentation.'
                                labelWidth={LABEL_WIDTH}
                                disabledMessage={this.state.waiting ? 'The Bucket Name as specified in Google Cloud Storage documentation.' : ''}
                                required
                            />
                            <TextBox<string>
                                getValue={() => this.state.serviceAccountKey}
                                saveValue={(value: string) => this.setState({ serviceAccountKey: value })}
                                label='Service Account Key'
                                helperText='The contents of the credentials file generated for your Google Service Account.'
                                labelWidth={LABEL_WIDTH}
                                disabledMessage={this.state.waiting ? 'The contents of the credentials file generated for your Google Service Account.' : ''}
                                multiline
                            />
                            {this.state.errorMessage && (
                                <div style={{
                                    color: '#f48f8d',
                                    margin: '12px',
                                    wordBreak: 'break-all',
                                    fontSize: '12px',
                                }}>
                                    {this.state.errorMessage}
                                </div>
                            )}
                        </div>
					</DialogContent>
				</StyledDialog>
            </div>
        )
    }

    public componentDidMount = () => {
        document.addEventListener('keydown', this.handleKeyDown, false)
    }

    public componentWillUnmount = () => {
        document.removeEventListener('keydown', this.handleKeyDown, false)
    }
}
