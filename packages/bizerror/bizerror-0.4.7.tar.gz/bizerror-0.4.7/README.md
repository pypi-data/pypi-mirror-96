# bizerror

Collections of common business errors.

## Install

```shell
pip install bizerror
```

## Installed command utils

- bizerror-generator

## Shipped exception classes

- OK
- SysError
    - UndefinedError
    - DatabaseError
    - CacheError
    - MessageQueueError
    - AnotherServiceError
- HttpError
    - RequestExpired
    - NotSupportedHttpMethod
    - ConfigError
    - MissingConfigItem
    - BadResponseContent
- DataError
    - TargetNotFound
- AuthError
    - AccountLockedError
    - AccountTemporaryLockedError
    - UserPasswordError
    - AppAuthFailed
    - TsExpiredError
    - AccountDisabledError
    - AccountStatusError
    - AccountRemovedError
    - LoginRequired
    - AccessDenied
    - UserDoesNotExist
    - BadUserToken
- TypeError

    - ParseJsonError
    - NotSupportedTypeToCast
- ParamError
    - MissingParameter
    - BadParameter
    - BadParameterType
    - StringTooShort
    - StringTooLong
- FormError
    - CaptchaOnlyAllowedOnce
    - CaptchaValidateFailed
    - RepeatedlySubmitForm
- LogicError
- CastFailedError
    - CastToIntegerFailed
    - CastToFloatFailed
    - CastToNumbericFailed
    - CastToBooleanFailed
    - CastToStringFailed

## Release Notes

### v0.4.7 2021-02-24

- Add BizError.update.
- Add CastFailedError.

### v0.4.6 2021-02-21

- Add BadResponseContent.

### v0.4.5 2021-02-19

- Add StringTooShort and StringTooLong.
- Fix bizerror.BizError(another_bizerror) problem.

### v0.4.2 2020-11-10

- Fix unicode encode/decode problems.
- Support python3 only.

### v0.4.1 2020-10-15

- Add UserDoesNotExist.
- Add BadUserToken.

### v0.4.0 2020-07-26

- Get error message by error class name, so that we can provide error message override function.

### v0.3.1 2020-07-19

- Fix xlsxhelper dependencies problem.

### v0.3.0 2020-07-19

- Add message parameters support.
- Add exception classes.
- Add class generator and tempalte maker.

### v0.2.3 2019-12-08

- Add NotSupportedTypeToCast error.

### v0.2.0 2019-11-07

- Fix get_error_message always use default language problem.
- Add BizError.MESSAGE classproperty.

### V0.2.0 2019-11-07

- Add auto generate mechanism.
- Add language support.


### v0.1.0

- Add BizError base class.
- Add some common errors.
