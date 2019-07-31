## Installation

You need a midi player, I used timidity:
```
sudo apt-get install freepats timidity timidity-interfaces-extra
```

```
sudo pip3 install -r requirements.txt
```

## Testing

To hear it I run:
```
./decompress.py && timidity output.mid
```
