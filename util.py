import bitio
import huffman
import pickle


def read_tree(tree_stream):
    '''Read a description of a Huffman tree from the given compressed
    tree stream, and use the pickle module to construct the tree object.
    Then, return the root node of the tree itself.

    Args:
      tree_stream: The compressed stream to read the tree from.

    Returns:
      A Huffman tree root constructed according to the given description.
    '''
    out = pickle.load(tree_stream)
    return out


def decode_byte(tree, bitreader):
    """
    Reads bits from the bit reader and traverses the tree from
    the root to a leaf. Once a leaf is reached, bits are no longer read
    and the value of that leaf is returned.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.
      tree: A Huffman tree.

    Returns:
      Next byte of the compressed bit stream.
    """
    byte = ''
    bit = bitreader.readbit()
    l = tree.getLeft()
    r = tree.getRight()

    if bit == 1:
        while not isinstance(r, huffman.TreeLeaf):
            bit = bitreader.readbit()
            if bit == 1:
                r = r.getRight()
            if bit == 0:
                r = r.getLeft()
        if isinstance(r, huffman.TreeLeaf):
            return r.getValue()

    if bit == 0:
        while not isinstance(l, huffman.TreeLeaf):
            bit = bitreader.readbit()
            if bit == 1:
                l = l.getRight()
            if bit == 0:
                l = l.getLeft()
        if isinstance(l, huffman.TreeLeaf):
            return l.getValue()


def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.
    '''
    tree = read_tree(compressed)
    encoded = bitio.BitReader(compressed)
    decoded = bitio.BitWriter(uncompressed)
    end_of_file = False
    try:
        while not end_of_file:

            byte = decode_byte(tree, encoded)
            if byte is None:
                end_of_file = True
            else:
                decoded.writebits(byte, 8)
    except EOFError:
        end_of_file = True


def write_tree(tree, tree_stream):
    '''Write the specified Huffman tree to the given tree_stream
    using pickle.

    Args:
      tree: A Huffman tree.
      tree_stream: The binary file to write the tree to.
    '''
    pickle.dump(tree, tree_stream)


def compress(tree, uncompressed, compressed):
    '''First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Flush the bitwriter after writing the entire compressed file.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    '''
    write_tree(tree, compressed)
    decoded = bitio.BitReader(uncompressed)
    encoded = bitio.BitWriter(compressed)
    table = huffman.make_encoding_table(tree)
    end_of_file = False

    try:
        while not end_of_file:
            byte = decoded.readbits(8)
            for x in table[byte]:
                encoded.writebit(x)
    except EOFError:
        for x in table[None]:
            encoded.writebit(x)
    encoded.flush()
