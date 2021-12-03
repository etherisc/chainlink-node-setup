import sys

ENCRYPT = 'encrypt'
DECRYPT = 'decrypt'
USAGE = 'usage: {} encrypt|decrypt password message'


def main():
    if len(sys.argv) != 4:
        print(USAGE.format(sys.argv[0]))
        sys.exit(1)

    action = sys.argv[1]
    if not action in [ENCRYPT, DECRYPT]:
        print('unexpected action {}. supported actions: {}'.format(action, ','.join([ENCRYPT, DECRYPT])))
        print(USAGE.format(sys.argv[0]))
        sys.exit(1)
    
    password = sys.argv[2]
    message = sys.argv[3]

    # TODO actual implementation
    print("action: '{}', password: '{}', message: '{}'".format(action, password, message))


if __name__ == "__main__":
    main()
