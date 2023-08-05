/*
**  Copyright (C) Optumi Inc - All rights reserved.
**
**  You may only use this code under license with Optumi Inc and any distribution or modification is strictly prohibited.
**  To receive a copy of the licensing terms please write to contact@optumi.com or visit us at http://www.optumi.com.
**/

import * as React from 'react';
import { Global } from '../Global';
import withStyles, { CSSProperties } from '@material-ui/core/styles/withStyles';
import { OutlinedInput, FormControl, InputAdornment, IconButton, FormHelperText } from '@material-ui/core';
import VisibilityIcon from '@material-ui/icons/Visibility';
import VisibilityOffIcon from '@material-ui/icons/VisibilityOff';

interface IProps {
    style?: CSSProperties
    getValue: () => string
    saveValue: (value: string) => Promise<string>
    checkForError: (value: string) => string
    password?: boolean
    placeholder?: string
    helperText?: string
    typingText?: string
    disabled?: boolean
    multiline?: boolean
}

interface IState {
    value: string
    hidePassword: boolean
    invalidTextMessage: string
    focused: boolean
}

export class FullWidthTextBox extends React.Component<IProps, IState> {
    StyledOutlinedInput: any
    StyledDisabledErrorOutlinedInput: any
    textField: React.RefObject<HTMLInputElement>

    constructor(props: IProps) {
        super(props);
        this.StyledOutlinedInput = this.getStyledOutlinedInput();
        this.StyledDisabledErrorOutlinedInput = this.getStyledDisabledErrorOutlinedInput();
        this.textField = React.createRef();
        var value = this.props.getValue();
        this.state = {
            value: value,
            hidePassword: true,
            invalidTextMessage: this.props.checkForError(value),
            focused: false,
        }
    }

    private getStyledOutlinedInput = () => {
        return withStyles({
            root: {
                backgroundColor: 'var(--jp-layout-color1)',
            },
            input: {
                fontSize: '12px',
                lineHeight: '14px',
                padding: '3px 6px 3px 6px',
            },
            adornedEnd: {
                paddingRight: '0px',
            },
            multiline: {
                padding: '0px',
            }, 
        }) (OutlinedInput);
    }

    private getStyledDisabledErrorOutlinedInput = () => {
        return withStyles({
            root: {
                backgroundColor: 'var(--jp-layout-color1)',
            },
            input: {
                fontSize: '12px',
                lineHeight: '14px',
                padding: '3px 6px 3px 6px',
            },
            adornedEnd: {
                paddingRight: '0px',
            },
            notchedOutline: {
                borderColor: '#f48f8d!important',
            },
            multiline: {
                padding: '0px',
            }, 
        }) (OutlinedInput);
    }

    private handleChange = (event: React.FormEvent<HTMLInputElement>) => {
        this.setState({ value: event.currentTarget.value });
        const checkResponse = this.props.checkForError(event.currentTarget.value)
        if (this.state.invalidTextMessage !== checkResponse) {
            this.setState({invalidTextMessage: checkResponse})
        }
    }

    private handleFocus = () => {
        this.setState({ focused: true });
    }

    private handleBlur = async () => {
        this.setState({ focused: false });
        if (this.state.invalidTextMessage === '') {
            const saveResponse =  await this.props.saveValue(this.state.value);
            if (this.state.invalidTextMessage !== saveResponse) {
                this.setState({ invalidTextMessage: saveResponse})
            } else {
                if (!this.props.multiline) this.setState({ value: '' });
            }
        }
    }
    
    public render = (): JSX.Element => {
        if (Global.shouldLogOnRender) console.log('FullWidthTextBoxRender (' + new Date().getSeconds() + ')');
        const StyledOutlinedInput = this.props.disabled && this.state.invalidTextMessage !== '' ? this.StyledDisabledErrorOutlinedInput : this.StyledOutlinedInput;
        return (
            <div style={Object.assign({display: 'inline-flex', width: '100%', padding: '0px'}, this.props.style)}>
                <FormControl
                    title={this.state.invalidTextMessage}
                    error={this.state.invalidTextMessage !== ''}
                    variant='outlined'
                    style={{width: '100%', margin: '0px 6px'}}
                >
                    <StyledOutlinedInput
                        disabled={this.props.disabled || false}
                        inputRef={this.textField}
                        value={this.state.value}
                        placeholder={this.state.focused ? this.props.placeholder : this.props.helperText}
                        onChange={this.handleChange}
                        onKeyDown={(event: React.KeyboardEvent) => {
                            if (((this.props.multiline == undefined || this.props.multiline == false) && event.key == 'Enter') || event.key == 'Escape') {
                                this.textField.current.blur();
                                if (this.state.invalidTextMessage === '') {
                                    this.textField.current.focus();
                                }
                            }
                        }}
                        onBlur={this.handleBlur}
                        onFocus={this.handleFocus}
                        multiline={this.props.multiline}
                        rows={this.state.value.split('\n').length}
                        type={this.props.password && this.state.hidePassword ? 'password' : 'text'}
                        endAdornment={
                            this.props.password && (
                                <InputAdornment position="end" title={this.state.hidePassword ? 'Show Password' : 'Hide Password'} style={{height: '20px', margin: '0px 3px 0px 0px'}}>
                                    <IconButton
                                        onClick={() => this.setState({hidePassword: !this.state.hidePassword})}
                                        style={{padding: '3px 3px 3px 0px'}}
                                    >
                                        {this.state.hidePassword ? (
                                            <VisibilityOffIcon style={{width: '14px', height: '14px'}} /> 
                                        ) : (
                                            <VisibilityIcon style={{width: '14px', height: '14px'}} />
                                        )}
                                    </IconButton>
                                </InputAdornment>
                            )
                        }
                    />
                    {(!this .props.disabled || (this.props.disabled && this.state.invalidTextMessage !== '')) ? (
                        <FormHelperText style={{fontSize: '10px', lineHeight: '10px', margin: '4px 6px', whiteSpace: 'nowrap', display: 'inline-flex'}}>
                            <div style={{flexGrow: 1}}>
                                {this.state.invalidTextMessage !== '' ? this.state.invalidTextMessage : ''}
                            </div>
                            <div>
                                {(this.state.invalidTextMessage === '' && this.state.focused && this.state.value !== '' ? this.props.typingText : '')}
                            </div>
                        </FormHelperText>
                    ) : (
                        <div style={{height: '9px'}}/>
                    )}
                </FormControl>
            </div>
        )
    }

    private handleMetadataChange = () => {
        var value = this.props.getValue();
        this.setState({ value: value, invalidTextMessage: this.props.checkForError(value) });
    }

    // Will be called automatically when the component is mounted
	componentDidMount = () => {
		Global.metadata.getMetadataChanged().connect(this.handleMetadataChange);
	}

	// Will be called automatically when the component is unmounted
	componentWillUnmount = () => {
        Global.metadata.getMetadataChanged().disconnect(this.handleMetadataChange);
    }

    public shouldComponentUpdate = (nextProps: IProps, nextState: IState): boolean => {
        try {
            if (JSON.stringify(this.props) != JSON.stringify(nextProps)) return true;
            if (JSON.stringify(this.state) != JSON.stringify(nextState)) return true;
            if (Global.shouldLogOnRender) console.log('SuppressedRender')
            return false;
        } catch (error) {
            return true;
        }
    }
}
