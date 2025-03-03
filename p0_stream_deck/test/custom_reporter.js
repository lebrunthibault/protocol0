// noinspection JSUnresolvedFunction,JSUnresolvedVariable

import { DefaultReporter, utils } from '@jest/reporters'
import chalk from 'chalk';

const getBufferedLog = (buffer, _config, globalConfig) => {
    const TITLE_INDENT = globalConfig.verbose ? '  ' : '    ';
    const CONSOLE_INDENT = TITLE_INDENT + '  ';
    const logEntries = buffer.reduce((output, { type, message, _origin }) => {
        message = message
            .split(/\n/)
            .map(line => CONSOLE_INDENT + line)
            .join('\n');
        if (type === 'warn') {
            message = chalk.yellow(message);
        } else if (type === 'error') {
            message = chalk.red(message);
        }
        return (
            output +
            message.trimEnd() +
            '\n'
        );
    }, '');
    return logEntries.trimEnd() + '\n';
};

class FocusedJestReporter extends DefaultReporter {
    // noinspection JSUnusedGlobalSymbols
    printTestFileHeader(_testPath, config, result) {
        this.log(utils.getResultHeader(result, this._globalConfig, config));

        if (result.console) {
            this.log(
                '  ' +
                'Console\n\n' +
                getBufferedLog(
                    result.console,
                    config,
                    this._globalConfig
                )
            );
        }
    }
}

// noinspection JSUnusedGlobalSymbols
export default FocusedJestReporter
